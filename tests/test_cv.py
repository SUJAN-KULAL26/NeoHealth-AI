"""Comprehensive unit tests for NeoHealth AI Computer Vision & Input Validation.

Validates:
1. Supported image format validation (JPG, JPEG, PNG)
2. Unsupported extension rejection
3. Missing file handling
4. Corrupted image detection
5. RGB conversion integrity
6. Grayscale to 3-channel RGB conversion
7. RGBA to 3-channel RGB conversion
8. Face detection result structure
9. Exactly-one-face decision logic
10. Zero-face decision logic
11. Multiple-face decision logic
12. Quality metric computation (dimensions, sharpness, brightness, contrast)
13. Quality metrics reported without arbitrary clinical thresholds
14. Skin mask generation and segmentation
15. Skin-region result structure and empty region handling
16. Inference gatekeeper integration (rejection on validation failure)
"""

import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image
import torch

from src.cv import (
    FaceCountStatus,
    FaceDetectionResult,
    ImageQualityResult,
    InputValidationStatus,
    MediaPipeFaceDetector,
    SkinDetectionResult,
    SkinDetectionStatus,
    compute_quality_metrics,
    detect_skin_region,
    evaluate_face_count,
    validate_input,
)
from src.inference import predict_image


class DummyModel(torch.nn.Module):
    """Dummy model returning deterministic logits for testing inference gating."""

    def __init__(self, num_classes: int = 6) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(3 * 224 * 224, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        # Return static logits favoring class 0 (Jaundice)
        logits = torch.zeros((batch_size, 6), dtype=torch.float32)
        logits[:, 0] = 5.0
        return logits


class MockFaceDetector:
    """Mock detector for simulating face detection outcomes without model assets."""

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


class TestInputValidation(unittest.TestCase):
    """Unit tests for format and data integrity validation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_01_supported_image_validation(self) -> None:
        """1. Supported image validation (.jpg, .jpeg, .png)."""
        for ext in [".jpg", ".jpeg", ".png"]:
            img = Image.new("RGB", (100, 100), color=(150, 120, 100))
            path = self.root_path / f"valid_sample{ext}"
            img.save(path)

            res = validate_input(path)
            self.assertTrue(res.is_valid)
            self.assertEqual(res.status, InputValidationStatus.VALID)
            self.assertIsNotNone(res.image_pil)
            self.assertIsNotNone(res.image_np)
            self.assertEqual(res.image_pil.size, (100, 100))
            self.assertEqual(res.image_np.shape, (100, 100, 3))

    def test_02_unsupported_extension(self) -> None:
        """2. Unsupported extension rejection."""
        unsupported_paths = [
            self.root_path / "document.pdf",
            self.root_path / "graphic.bmp",
            self.root_path / "photo.webp",
            self.root_path / "notes.txt",
        ]
        for p in unsupported_paths:
            p.write_bytes(b"dummy content")
            res = validate_input(p)
            self.assertFalse(res.is_valid)
            self.assertEqual(res.status, InputValidationStatus.INVALID_FORMAT)
            self.assertIn("Unsupported image extension", res.message)

    def test_03_missing_file(self) -> None:
        """3. Missing file handling."""
        nonexistent = self.root_path / "does_not_exist.jpg"
        res = validate_input(nonexistent)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, InputValidationStatus.FILE_NOT_FOUND)
        self.assertIn("File not found", res.message)

    def test_04_corrupted_image(self) -> None:
        """4. Corrupted image detection."""
        corrupt_path = self.root_path / "corrupted.jpg"
        # Write random non-image bytes to a .jpg file
        corrupt_path.write_bytes(b"corrupt header and garbage data 1234567890")
        res = validate_input(corrupt_path)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, InputValidationStatus.INVALID_IMAGE)
        self.assertIn("Failed to decode", res.message)

    def test_05_rgb_conversion(self) -> None:
        """5. RGB conversion from PIL and NumPy."""
        img = Image.new("RGB", (64, 64), color=(200, 100, 50))
        res_pil = validate_input(img)
        self.assertTrue(res_pil.is_valid)
        self.assertEqual(res_pil.image_pil.mode, "RGB")
        self.assertEqual(res_pil.image_np.shape, (64, 64, 3))

    def test_06_grayscale_conversion(self) -> None:
        """6. Grayscale conversion to 3-channel RGB."""
        gray_img = Image.new("L", (80, 80), color=128)
        res = validate_input(gray_img)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.image_pil.mode, "RGB")
        self.assertEqual(res.image_np.shape, (80, 80, 3))
        # Grayscale converted to RGB should have identical channel values
        self.assertEqual(res.image_np[0, 0, 0], res.image_np[0, 0, 1])
        self.assertEqual(res.image_np[0, 0, 1], res.image_np[0, 0, 2])

    def test_07_rgba_conversion(self) -> None:
        """7. RGBA conversion to 3-channel RGB (alpha channel stripped)."""
        rgba_img = Image.new("RGBA", (50, 50), color=(100, 150, 200, 128))
        res = validate_input(rgba_img)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.image_pil.mode, "RGB")
        self.assertEqual(res.image_np.shape, (50, 50, 3))


class TestFaceDetection(unittest.TestCase):
    """Unit tests for face detection logic and structured results."""

    def test_08_face_detection_result_structure(self) -> None:
        """8. Face detection result structure."""
        boxes = [{"origin_x": 10, "origin_y": 20, "width": 50, "height": 60, "score": 0.98}]
        res = FaceDetectionResult(
            status=FaceCountStatus.EXACTLY_ONE_FACE,
            is_valid=True,
            face_count=1,
            boxes=boxes,
            message="Single face verified.",
        )
        d = res.to_dict()
        self.assertEqual(d["status"], "EXACTLY_ONE_FACE")
        self.assertTrue(d["is_valid"])
        self.assertEqual(d["face_count"], 1)
        self.assertEqual(len(d["boxes"]), 1)
        self.assertEqual(d["boxes"][0]["origin_x"], 10)

    def test_09_exactly_one_face_decision_logic(self) -> None:
        """9. Exactly-one-face decision logic."""
        status = evaluate_face_count(1)
        self.assertEqual(status, FaceCountStatus.EXACTLY_ONE_FACE)

    def test_10_zero_face_decision(self) -> None:
        """10. Zero-face decision logic."""
        status = evaluate_face_count(0)
        self.assertEqual(status, FaceCountStatus.NO_FACE_DETECTED)

    def test_11_multiple_face_decision(self) -> None:
        """11. Multiple-face decision logic."""
        for count in [2, 3, 5]:
            status = evaluate_face_count(count)
            self.assertEqual(status, FaceCountStatus.MULTIPLE_FACES_DETECTED)

    def test_mediapipe_missing_model_asset_raises_error(self) -> None:
        """Verify detector raises clear FileNotFoundError when model asset is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = Path(tmp) / "nonexistent.tflite"
            with self.assertRaises(FileNotFoundError) as ctx:
                MediaPipeFaceDetector(model_asset_path=missing_path)
            self.assertIn("model asset not found", str(ctx.exception).lower())


class TestImageQuality(unittest.TestCase):
    """Unit tests for objective quality metric computation."""

    def test_12_quality_metric_calculation(self) -> None:
        """12. Quality metric calculation (Laplacian variance, brightness, contrast, dimensions)."""
        # Create image with high-contrast sharp edges
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[25:75, 25:75, :] = 255

        res = compute_quality_metrics(arr)
        self.assertIsInstance(res, ImageQualityResult)
        m = res.metrics
        self.assertEqual(m["width"], 100.0)
        self.assertEqual(m["height"], 100.0)
        self.assertEqual(m["channels"], 3.0)
        self.assertGreater(m["sharpness_laplacian_var"], 0.0)
        self.assertGreater(m["mean_brightness"], 0.0)
        self.assertGreater(m["contrast_std"], 0.0)
        self.assertEqual(m["min_brightness"], 0.0)
        self.assertEqual(m["max_brightness"], 255.0)

    def test_13_quality_metrics_without_arbitrary_thresholds(self) -> None:
        """13. Quality metrics reported without claiming arbitrary clinical validity."""
        blank_arr = np.full((50, 50, 3), 128, dtype=np.uint8)
        res = compute_quality_metrics(blank_arr)

        self.assertEqual(res.status, "quality_unassessed")
        self.assertFalse(res.is_assessed)
        self.assertIn("clinical assessment requires experimentally established thresholds", res.message)


class TestSkinDetection(unittest.TestCase):
    """Unit tests for skin region segmentation and bounding box extraction."""

    def test_14_skin_mask_generation(self) -> None:
        """14. Skin mask generation and segmentation on cutaneous pixels."""
        # Create synthetic skin-toned image (RGB [210, 160, 130])
        skin_img = np.zeros((100, 100, 3), dtype=np.uint8)
        skin_img[20:80, 20:80] = [210, 160, 130]

        res = detect_skin_region(skin_img)
        self.assertTrue(res.has_skin)
        self.assertEqual(res.status, SkinDetectionStatus.SKIN_REGION_DETECTED)
        self.assertGreater(res.skin_pixels, 0)
        self.assertGreater(res.coverage_ratio, 0.0)
        self.assertIsNotNone(res.bounding_box)
        self.assertEqual(res.mask.shape, (100, 100))

    def test_15_skin_region_result_structure(self) -> None:
        """15. Skin-region result structure and empty region handling."""
        # Pure blue image (zero skin content)
        blue_img = np.zeros((80, 80, 3), dtype=np.uint8)
        blue_img[:, :] = [0, 0, 255]

        res = detect_skin_region(blue_img)
        self.assertFalse(res.has_skin)
        self.assertEqual(res.status, SkinDetectionStatus.SKIN_REGION_UNAVAILABLE)
        self.assertEqual(res.skin_pixels, 0)
        self.assertEqual(res.coverage_ratio, 0.0)
        self.assertIsNone(res.bounding_box)

        d = res.to_dict()
        self.assertEqual(d["status"], "SKIN_REGION_UNAVAILABLE")
        self.assertFalse(d["has_skin"])


class TestInferenceGatekeeper(unittest.TestCase):
    """Unit tests for the end-to-end inference gatekeeper in src/inference.py."""

    def setUp(self) -> None:
        self.model = DummyModel()
        self.device = torch.device("cpu")
        self.model.eval()

    def test_16_gatekeeper_rejects_on_unsupported_format(self) -> None:
        """16. Gatekeeper rejects unsupported format before running EfficientNet."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"not an image")
            pdf_path = Path(f.name)

        try:
            result = predict_image(pdf_path, self.model, self.device)
            self.assertFalse(result["is_valid"])
            self.assertFalse(result["validation_passed"])
            self.assertEqual(result["status"], "INVALID_FORMAT")
            self.assertNotIn("prediction", result)
        finally:
            pdf_path.unlink(missing_ok=True)

    def test_17_gatekeeper_rejects_on_no_face(self) -> None:
        """17. Gatekeeper rejects input when zero faces are detected."""
        detector = MockFaceDetector(face_count=0)
        # Synthetic skin image
        img = np.full((100, 100, 3), [210, 160, 130], dtype=np.uint8)

        result = predict_image(img, self.model, self.device, face_detector=detector)
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "NO_FACE_DETECTED")
        self.assertNotIn("prediction", result)

    def test_18_gatekeeper_rejects_on_multiple_faces(self) -> None:
        """18. Gatekeeper rejects input when multiple faces are detected."""
        detector = MockFaceDetector(face_count=2)
        img = np.full((100, 100, 3), [210, 160, 130], dtype=np.uint8)

        result = predict_image(img, self.model, self.device, face_detector=detector)
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "MULTIPLE_FACES_DETECTED")
        self.assertNotIn("prediction", result)

    def test_19_gatekeeper_rejects_on_unavailable_skin(self) -> None:
        """19. Gatekeeper rejects input when no skin tissue is detected."""
        detector = MockFaceDetector(face_count=1)
        # Pure blue image (no skin pixels)
        blue_img = np.zeros((100, 100, 3), dtype=np.uint8)
        blue_img[:, :] = [0, 0, 255]

        result = predict_image(blue_img, self.model, self.device, face_detector=detector)
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "SKIN_REGION_UNAVAILABLE")
        self.assertNotIn("prediction", result)

    def test_20_gatekeeper_passes_valid_image(self) -> None:
        """20. Gatekeeper executes model prediction when all CV gates pass."""
        detector = MockFaceDetector(face_count=1)
        # Synthetic skin image
        skin_img = np.full((100, 100, 3), [210, 160, 130], dtype=np.uint8)

        result = predict_image(skin_img, self.model, self.device, face_detector=detector)
        self.assertIn("prediction", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)
        self.assertIn("validation_details", result)
        self.assertEqual(result["validation_details"]["face_detection"]["face_count"], 1)
        self.assertTrue(result["validation_details"]["skin_detection"]["has_skin"])


if __name__ == "__main__":
    unittest.main()
