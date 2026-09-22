"""Comprehensive unit tests for NeoHealth AI model loading and inference pipeline.

Validates:
A. Missing checkpoint handling (FileNotFoundError and MODEL_NOT_FOUND structured status)
B. Invalid/corrupt checkpoint handling (RuntimeError and MODEL_LOAD_FAILED structured status)
C. Invalid checkpoint metadata (mismatched num_classes, mismatched class names, missing keys)
D. Valid synthetic checkpoint loading, eval mode verification, and state dict integrity
E. High-confidence prediction evaluation (confidence >= 0.70 -> "screening_result")
F. Low-confidence prediction evaluation (confidence < 0.70 -> "uncertain_review_required")
G. Probability dictionary structure (all canonical classes, float values, sum ~= 1.0)
H. Medical screening disclaimer presence on both success and failure results
I. CV gatekeeper preservation (format, face count, and skin gates reject before model loading)
"""

import math
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch
import torch.nn as nn

from src.config import CLASS_NAMES, DISCLAIMER_TEXT, NUM_CLASSES
from src.cv import FaceCountStatus, FaceDetectionResult, evaluate_face_count
from src.inference import load_model, predict_image
from src.models.efficientnet import create_efficientnet_b0


class MockFaceDetector:
    """Mock detector for simulating face detection outcomes in inference tests."""

    def __init__(self, face_count: int = 1) -> None:
        self.face_count = face_count

    def detect(self, image: np.ndarray) -> FaceDetectionResult:
        boxes: List[Dict[str, Any]] = [
            {"origin_x": 50 * i, "origin_y": 50 * i, "width": 80, "height": 80, "score": 0.95}
            for i in range(self.face_count)
        ]
        status = evaluate_face_count(self.face_count)
        is_valid = status == FaceCountStatus.EXACTLY_ONE_FACE
        return FaceDetectionResult(
            status=status,
            is_valid=is_valid,
            face_count=self.face_count,
            boxes=boxes,
            message=f"Mock detector detected {self.face_count} face(s).",
        )


class DeterministicLogitsModel(nn.Module):
    """Deterministic model producing fixed logits for testing confidence branching."""

    def __init__(self, logits: List[float]) -> None:
        super().__init__()
        self.register_buffer("fixed_logits", torch.tensor([logits], dtype=torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        return self.fixed_logits.expand(batch_size, -1)


class TestModelLoadingAndValidation(unittest.TestCase):
    """Unit tests for load_model() error handling and checkpoint validation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_A_missing_checkpoint_raises_file_not_found(self) -> None:
        """A. load_model() raises FileNotFoundError for nonexistent paths."""
        nonexistent = self.root / "does_not_exist.pth"
        with self.assertRaises(FileNotFoundError) as ctx:
            load_model(nonexistent)
        self.assertIn("not found", str(ctx.exception).lower())

    def test_B_corrupt_checkpoint_raises_runtime_error(self) -> None:
        """B. load_model() raises RuntimeError when checkpoint file is corrupted."""
        corrupt_path = self.root / "corrupted.pth"
        corrupt_path.write_bytes(b"NOT_A_VALID_PYTORCH_CHECKPOINT_DATA")
        with self.assertRaises(RuntimeError) as ctx:
            load_model(corrupt_path)
        self.assertIn("failed to load checkpoint", str(ctx.exception).lower())

    def test_C1_non_dict_checkpoint_raises_value_error(self) -> None:
        """C1. load_model() raises ValueError if checkpoint is not a dictionary."""
        bad_path = self.root / "non_dict.pth"
        torch.save(["not", "a", "dict"], bad_path)
        with self.assertRaises(ValueError) as ctx:
            load_model(bad_path)
        self.assertIn("expected a dictionary", str(ctx.exception).lower())

    def test_C2_missing_state_dict_raises_value_error(self) -> None:
        """C2. load_model() raises ValueError if model_state_dict is missing."""
        bad_path = self.root / "missing_state_dict.pth"
        torch.save({"num_classes": NUM_CLASSES, "classes": CLASS_NAMES}, bad_path)
        with self.assertRaises(ValueError) as ctx:
            load_model(bad_path)
        self.assertIn("missing required key 'model_state_dict'", str(ctx.exception).lower())

    def test_C3_mismatched_num_classes_raises_value_error(self) -> None:
        """C3. load_model() raises ValueError if num_classes != NUM_CLASSES (6)."""
        bad_path = self.root / "wrong_num_classes.pth"
        base_model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        torch.save({
            "model_state_dict": base_model.state_dict(),
            "num_classes": 5,
            "classes": CLASS_NAMES,
        }, bad_path)
        with self.assertRaises(ValueError) as ctx:
            load_model(bad_path)
        self.assertIn("num_classes mismatch", str(ctx.exception).lower())

    def test_C4_mismatched_classes_raises_value_error(self) -> None:
        """C4. load_model() raises ValueError if class list does not match canonical CLASS_NAMES."""
        bad_path = self.root / "wrong_classes.pth"
        base_model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        torch.save({
            "model_state_dict": base_model.state_dict(),
            "num_classes": NUM_CLASSES,
            "classes": ("Jaundice", "Normal", "WrongClass1", "WrongClass2", "WrongClass3", "WrongClass4"),
        }, bad_path)
        with self.assertRaises(ValueError) as ctx:
            load_model(bad_path)
        self.assertIn("classes mismatch", str(ctx.exception).lower())

    def test_D_valid_synthetic_checkpoint_loads_successfully(self) -> None:
        """D. load_model() successfully loads a valid synthetic checkpoint in eval mode."""
        valid_path = self.root / "valid_model.pth"
        base_model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        torch.save({
            "model_state_dict": base_model.state_dict(),
            "num_classes": NUM_CLASSES,
            "classes": CLASS_NAMES,
            "best_val_accuracy": 0.88,
        }, valid_path)

        loaded_model, device = load_model(valid_path)
        self.assertIsInstance(loaded_model, nn.Module)
        self.assertFalse(loaded_model.training)


class TestInferencePredictionAndConfidence(unittest.TestCase):
    """Unit tests for predict_image() pipeline, confidence branching, and auto-resolution."""

    def setUp(self) -> None:
        self.skin_img = np.full((100, 100, 3), [210, 160, 130], dtype=np.uint8)
        self.face_detector = MockFaceDetector(face_count=1)

    def test_A_auto_resolution_missing_checkpoint_returns_structured_failure(self) -> None:
        """A. predict_image(model=None) returns MODEL_NOT_FOUND when checkpoint is missing."""
        missing_path = Path("nonexistent_models_dir") / "missing.pth"
        result = predict_image(
            self.skin_img,
            model=None,
            face_detector=self.face_detector,
            model_path=missing_path,
        )
        self.assertEqual(result["status"], "MODEL_NOT_FOUND")
        self.assertFalse(result["is_valid"])
        self.assertFalse(result["validation_passed"])
        self.assertIn("disclaimer", result)
        self.assertEqual(result["disclaimer"], DISCLAIMER_TEXT)
        self.assertNotIn("prediction", result)

    def test_B_auto_resolution_corrupt_checkpoint_returns_structured_failure(self) -> None:
        """B. predict_image(model=None) returns MODEL_LOAD_FAILED when checkpoint is corrupted."""
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as f:
            f.write(b"CORRUPTED_BYTES")
            corrupt_path = Path(f.name)

        try:
            result = predict_image(
                self.skin_img,
                model=None,
                face_detector=self.face_detector,
                model_path=corrupt_path,
            )
            self.assertEqual(result["status"], "MODEL_LOAD_FAILED")
            self.assertFalse(result["is_valid"])
            self.assertFalse(result["validation_passed"])
            self.assertIn("disclaimer", result)
            self.assertNotIn("prediction", result)
        finally:
            corrupt_path.unlink(missing_ok=True)

    def test_D_auto_resolution_valid_synthetic_checkpoint_predicts_successfully(self) -> None:
        """D. predict_image(model=None) resolves model and completes inference when checkpoint is valid."""
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as f:
            temp_path = Path(f.name)

        try:
            base_model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
            torch.save({
                "model_state_dict": base_model.state_dict(),
                "num_classes": NUM_CLASSES,
                "classes": CLASS_NAMES,
            }, temp_path)

            result = predict_image(
                self.skin_img,
                model=None,
                face_detector=self.face_detector,
                model_path=temp_path,
            )
            self.assertIn("prediction", result)
            self.assertIn("confidence", result)
            self.assertIn(result["status"], ["screening_result", "uncertain_review_required"])
            self.assertEqual(result["disclaimer"], DISCLAIMER_TEXT)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_E_high_confidence_prediction(self) -> None:
        """E. Prediction with confidence >= 0.70 yields is_confident=True and status='screening_result'."""
        # Strong logits favoring class 0 (Jaundice) -> softmax > 0.99
        high_conf_model = DeterministicLogitsModel([10.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        device = torch.device("cpu")

        result = predict_image(
            self.skin_img,
            model=high_conf_model,
            device=device,
            face_detector=self.face_detector,
        )

        self.assertEqual(result["prediction"], "Jaundice")
        self.assertGreaterEqual(result["confidence"], 0.70)
        self.assertTrue(result["is_confident"])
        self.assertEqual(result["status"], "screening_result")
        self.assertEqual(result["disclaimer"], DISCLAIMER_TEXT)

    def test_F_low_confidence_prediction(self) -> None:
        """F. Prediction with confidence < 0.70 yields is_confident=False and status='uncertain_review_required'."""
        # Equal logits across all 6 classes -> softmax is 1/6 (~0.1667 < 0.70)
        low_conf_model = DeterministicLogitsModel([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        device = torch.device("cpu")

        result = predict_image(
            self.skin_img,
            model=low_conf_model,
            device=device,
            face_detector=self.face_detector,
        )

        self.assertLess(result["confidence"], 0.70)
        self.assertFalse(result["is_confident"])
        self.assertEqual(result["status"], "uncertain_review_required")
        self.assertEqual(result["disclaimer"], DISCLAIMER_TEXT)

    def test_G_probability_dictionary_properties(self) -> None:
        """G. Probabilities dict contains all six canonical classes, float values, and sums to ~1.0."""
        model = DeterministicLogitsModel([3.0, 1.5, 0.5, 0.2, 0.1, 0.0])
        device = torch.device("cpu")

        result = predict_image(
            self.skin_img,
            model=model,
            device=device,
            face_detector=self.face_detector,
        )

        probs = result["probabilities"]
        self.assertEqual(len(probs), 6)
        for class_name in CLASS_NAMES:
            self.assertIn(class_name, probs)
            self.assertIsInstance(probs[class_name], float)
            self.assertGreaterEqual(probs[class_name], 0.0)
            self.assertLessEqual(probs[class_name], 1.0)

        total_prob = sum(probs.values())
        self.assertTrue(math.isclose(total_prob, 1.0, abs_tol=1e-4))

    def test_H_disclaimer_present_on_all_outputs(self) -> None:
        """H. Successful prediction explicitly contains the locked medical disclaimer."""
        model = DeterministicLogitsModel([5.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        device = torch.device("cpu")

        result = predict_image(
            self.skin_img,
            model=model,
            device=device,
            face_detector=self.face_detector,
        )
        self.assertEqual(result.get("disclaimer"), DISCLAIMER_TEXT)

    def test_I_cv_gatekeeper_rejects_before_model_loading(self) -> None:
        """I. CV gatekeeper failures abort before any model resolution is attempted."""
        # 1. Invalid file extension rejects at Gate 1 even when model is None
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            txt_path = Path(f.name)

        try:
            result = predict_image(txt_path, model=None)
            self.assertEqual(result["status"], "INVALID_FORMAT")
            self.assertFalse(result["is_valid"])
            self.assertNotIn("prediction", result)
        finally:
            txt_path.unlink(missing_ok=True)

        # 2. Zero face detected rejects at Gate 2 without loading model
        no_face_detector = MockFaceDetector(face_count=0)
        result_no_face = predict_image(
            self.skin_img,
            model=None,
            face_detector=no_face_detector,
        )
        self.assertEqual(result_no_face["status"], "NO_FACE_DETECTED")
        self.assertFalse(result_no_face["is_valid"])
        self.assertNotIn("prediction", result_no_face)

        # 3. Multiple faces detected rejects at Gate 2 without loading model
        multi_face_detector = MockFaceDetector(face_count=2)
        result_multi = predict_image(
            self.skin_img,
            model=None,
            face_detector=multi_face_detector,
        )
        self.assertEqual(result_multi["status"], "MULTIPLE_FACES_DETECTED")
        self.assertFalse(result_multi["is_valid"])
        self.assertNotIn("prediction", result_multi)

        # 4. Skin tissue unavailable rejects at Gate 4 without loading model
        blue_img = np.zeros((100, 100, 3), dtype=np.uint8)
        blue_img[:, :] = [0, 0, 255]
        result_blue = predict_image(
            blue_img,
            model=None,
            face_detector=self.face_detector,
        )
        self.assertEqual(result_blue["status"], "SKIN_REGION_UNAVAILABLE")
        self.assertFalse(result_blue["is_valid"])
        self.assertNotIn("prediction", result_blue)


if __name__ == "__main__":
    unittest.main()
