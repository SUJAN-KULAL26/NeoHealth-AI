"""Comprehensive unit tests for NeoHealth AI model evaluation architecture.

Validates:
1. Perfect six-class predictions (accuracy=1.0, 6x6 confusion matrix, diagonal check)
2. Known imperfect predictions (exact verification of macro/weighted precision, recall, F1)
3. Per-class metrics dictionary covering all six canonical classes
4. Support tracking including safe handling of zero-support classes
5. Confusion matrix structure (exact 6x6 shape, CLASS_NAMES ordering)
6. zero_division safety across unpredicted classes
7. ROC/AUC calculation when mathematically applicable
8. ROC/AUC unavailable handling (safe None/unavailable without fabricating values)
9. Probability dimension and shape validation
10. Label validity enforcement (rejection of out-of-bound indices and non-canonical strings)
11. Accurate sample count reporting
12. Checkpoint and DataLoader evaluation without modifying model weights
"""

import math
import tempfile
import unittest
from pathlib import Path
from typing import List

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.config import CLASS_NAMES, NUM_CLASSES
from src.evaluate import (
    EvaluationResult,
    compute_metrics,
    evaluate_checkpoint,
    evaluate_model,
)
from src.models.efficientnet import create_efficientnet_b0


class TestEvaluationMetrics(unittest.TestCase):
    """Unit tests for objective metric calculation logic."""

    def test_01_perfect_six_class_predictions(self) -> None:
        """1. Perfect predictions yield accuracy=1.0, macro metrics=1.0, and pure diagonal 6x6 CM."""
        # 12 samples: 2 per class for all 6 canonical classes
        y_true = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
        y_pred = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]

        res = compute_metrics(y_true, y_pred)
        d = res.to_dict()

        self.assertEqual(d["num_samples"], 12)
        self.assertEqual(d["accuracy"], 1.0)
        self.assertEqual(d["precision"]["macro"], 1.0)
        self.assertEqual(d["recall"]["macro"], 1.0)
        self.assertEqual(d["f1"]["macro"], 1.0)

        # Check 6x6 confusion matrix diagonal
        cm = d["confusion_matrix"]
        self.assertEqual(len(cm), 6)
        for i in range(6):
            self.assertEqual(len(cm[i]), 6)
            for j in range(6):
                if i == j:
                    self.assertEqual(cm[i][j], 2)
                else:
                    self.assertEqual(cm[i][j], 0)

    def test_02_known_imperfect_predictions(self) -> None:
        """2. Known imperfect predictions yield analytically exact metric scores."""
        # 6 samples: 1 per class.
        # Target 5 is misclassified as 0.
        y_true = [0, 1, 2, 3, 4, 5]
        y_pred = [0, 1, 2, 3, 4, 0]

        res = compute_metrics(y_true, y_pred)
        d = res.to_dict()

        # Accuracy: 5/6 ~ 0.833333
        self.assertTrue(math.isclose(d["accuracy"], 5 / 6, abs_tol=1e-5))

        # Precision:
        # Class 0: 1 TP / 2 Pred = 0.5
        # Classes 1-4: 1 TP / 1 Pred = 1.0
        # Class 5: 0 Pred = 0.0 (zero_division=0)
        # Macro Precision: (0.5 + 4*1.0 + 0.0) / 6 = 4.5 / 6 = 0.75
        self.assertTrue(math.isclose(d["precision"]["macro"], 0.75, abs_tol=1e-5))
        self.assertTrue(math.isclose(d["precision"]["weighted"], 0.75, abs_tol=1e-5))

        # Recall:
        # Classes 0-4: 1 TP / 1 Target = 1.0
        # Class 5: 0 TP / 1 Target = 0.0
        # Macro Recall: (5*1.0 + 0.0) / 6 = 5/6 ~ 0.833333
        self.assertTrue(math.isclose(d["recall"]["macro"], 5 / 6, abs_tol=1e-5))
        self.assertTrue(math.isclose(d["recall"]["weighted"], 5 / 6, abs_tol=1e-5))

        # F1:
        # Class 0: 2*(0.5*1.0)/(0.5+1.0) = 2/3 ~ 0.666667
        # Classes 1-4: 1.0
        # Class 5: 0.0
        # Macro F1: (2/3 + 4*1.0 + 0.0) / 6 = (14/3) / 6 = 7/9 ~ 0.777778
        self.assertTrue(math.isclose(d["f1"]["macro"], 7 / 9, abs_tol=1e-5))
        self.assertTrue(math.isclose(d["f1"]["weighted"], 7 / 9, abs_tol=1e-5))

    def test_03_per_class_metrics_contain_all_canonical_classes(self) -> None:
        """3. Per-class metrics dictionary contains all six canonical class names."""
        y_true = [0, 1, 2, 3, 4, 5]
        y_pred = [0, 1, 2, 3, 4, 5]

        res = compute_metrics(y_true, y_pred)
        d = res.to_dict()

        for class_name in CLASS_NAMES:
            self.assertIn(class_name, d["precision"]["per_class"])
            self.assertIn(class_name, d["recall"]["per_class"])
            self.assertIn(class_name, d["f1"]["per_class"])
            self.assertIn(class_name, d["support"])

    def test_04_support_and_zero_support_classes(self) -> None:
        """4. Support safely reflects class counts and reports 0 for unrepresented classes."""
        # Only Jaundice (0) and Atopic Dermatitis (1) present in targets
        y_true = [0, 0, 1, 1]
        y_pred = [0, 1, 1, 1]

        res = compute_metrics(y_true, y_pred)
        d = res.to_dict()

        self.assertEqual(d["support"]["Jaundice"], 2)
        self.assertEqual(d["support"]["Atopic Dermatitis"], 2)
        self.assertEqual(d["support"]["Impetigo"], 0)
        self.assertEqual(d["support"]["Cradle Cap"], 0)
        self.assertEqual(d["support"]["Neonatal Acne"], 0)
        self.assertEqual(d["support"]["Normal"], 0)

        # Unrepresented classes report 0.0 metrics without crashing
        self.assertEqual(d["precision"]["per_class"]["Impetigo"], 0.0)
        self.assertEqual(d["recall"]["per_class"]["Impetigo"], 0.0)
        self.assertEqual(d["f1"]["per_class"]["Impetigo"], 0.0)

    def test_05_confusion_matrix_shape_and_order(self) -> None:
        """5. Confusion matrix has exact 6x6 dimensions matching CLASS_NAMES order."""
        y_true = [0, 2]
        y_pred = [0, 3]

        res = compute_metrics(y_true, y_pred)
        cm = res.confusion_matrix

        self.assertEqual(len(cm), 6)
        for row in cm:
            self.assertEqual(len(row), 6)

        # Row 0 (Jaundice): predicted Jaundice (col 0) -> 1
        self.assertEqual(cm[0][0], 1)
        # Row 2 (Impetigo): predicted Cradle Cap (col 3) -> 1
        self.assertEqual(cm[2][3], 1)

    def test_06_zero_division_safety(self) -> None:
        """6. zero_division=0 prevents ZeroDivisionError when a class is never predicted."""
        # Class 0 is never predicted
        y_true = [0, 1, 1]
        y_pred = [1, 1, 1]

        res = compute_metrics(y_true, y_pred)
        d = res.to_dict()

        # Class 0 precision should be 0.0 without raising exception
        self.assertEqual(d["precision"]["per_class"]["Jaundice"], 0.0)
        self.assertEqual(d["recall"]["per_class"]["Jaundice"], 0.0)
        self.assertEqual(d["f1"]["per_class"]["Jaundice"], 0.0)

    def test_07_roc_auc_multiclass_available(self) -> None:
        """7. ROC/AUC is successfully computed when all classes have valid positive/negative samples."""
        # 12 samples: 2 per class across all 6 classes
        y_true = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
        y_pred = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]

        # Synthetic probabilities heavily favoring true class
        probs = np.full((12, 6), 0.04, dtype=np.float64)
        for idx, target in enumerate(y_true):
            probs[idx, target] = 0.80

        res = compute_metrics(y_true, y_pred, y_probs=probs)
        roc = res.to_dict()["roc_auc"]

        self.assertTrue(roc["available"])
        self.assertIsNotNone(roc["macro"])
        self.assertGreater(roc["macro"], 0.90)
        self.assertEqual(len(roc["per_class"]), 6)
        for cls_name in CLASS_NAMES:
            self.assertIsNotNone(roc["per_class"][cls_name])
            self.assertGreaterEqual(roc["per_class"][cls_name], 0.0)

    def test_08_roc_auc_unavailable_when_class_has_zero_positives(self) -> None:
        """8. ROC/AUC safely returns available=False and macro=None without fabricating values."""
        # Normal (class 5) has zero samples in y_true
        y_true = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
        y_pred = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
        probs = np.full((10, 6), 1 / 6, dtype=np.float64)

        res = compute_metrics(y_true, y_pred, y_probs=probs)
        roc = res.to_dict()["roc_auc"]

        self.assertFalse(roc["available"])
        self.assertIsNone(roc["macro"])
        self.assertIsNone(roc["per_class"]["Normal"])
        self.assertIn("unavailable", roc["message"].lower())

    def test_09_probability_dimension_validation(self) -> None:
        """9. Invalid probability matrix shapes/dimensions are rejected with ValueError."""
        y_true = [0, 1, 2]
        y_pred = [0, 1, 2]

        # 1D array
        with self.assertRaises(ValueError):
            compute_metrics(y_true, y_pred, y_probs=np.array([0.1, 0.2, 0.7]))

        # Wrong column count (4 columns instead of 6)
        with self.assertRaises(ValueError):
            compute_metrics(y_true, y_pred, y_probs=np.zeros((3, 4)))

        # Row count mismatch (5 rows for 3 samples)
        with self.assertRaises(ValueError):
            compute_metrics(y_true, y_pred, y_probs=np.zeros((5, 6)))

    def test_10_label_validity_enforcement(self) -> None:
        """10. Non-canonical strings and out-of-range integer indices are rejected."""
        y_pred = [0, 1, 2]

        # Out-of-bounds integer index
        with self.assertRaises(ValueError):
            compute_metrics([0, 1, 6], y_pred)

        with self.assertRaises(ValueError):
            compute_metrics([-1, 0, 1], y_pred)

        # Non-canonical class name string
        with self.assertRaises(ValueError):
            compute_metrics(["Jaundice", "Normal", "Melanoma"], y_pred)

    def test_11_string_and_integer_label_equivalence(self) -> None:
        """11. String labels and integer label indices yield identical evaluation metrics."""
        int_true = [0, 1, 2, 3, 4, 5]
        int_pred = [0, 1, 2, 3, 4, 5]

        str_true = list(CLASS_NAMES)
        str_pred = list(CLASS_NAMES)

        res_int = compute_metrics(int_true, int_pred).to_dict()
        res_str = compute_metrics(str_true, str_pred).to_dict()

        self.assertEqual(res_int["accuracy"], res_str["accuracy"])
        self.assertEqual(res_int["f1"], res_str["f1"])
        self.assertEqual(res_int["confusion_matrix"], res_str["confusion_matrix"])

    def test_12_num_samples_reporting(self) -> None:
        """12. Result dictionary reports accurate sample count."""
        y_true = [0, 1, 2, 3, 4, 5, 0]
        y_pred = [0, 1, 2, 3, 4, 5, 0]

        res = compute_metrics(y_true, y_pred)
        self.assertEqual(res.num_samples, 7)
        self.assertEqual(res.to_dict()["num_samples"], 7)


class TestModelAndCheckpointEvaluation(unittest.TestCase):
    """Unit tests for evaluate_model() and evaluate_checkpoint()."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_13_evaluate_model_preserves_weights(self) -> None:
        """13. evaluate_model() does not alter model parameters during evaluation."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        model.eval()

        # Capture initial parameter snapshot
        initial_params = [p.clone() for p in model.parameters()]

        # Synthetic DataLoader
        images = torch.randn(4, 3, 224, 224)
        targets = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
        dataset = TensorDataset(images, targets)
        loader = DataLoader(dataset, batch_size=2, shuffle=False)

        res = evaluate_model(model, loader, device=torch.device("cpu"))
        self.assertIsInstance(res, EvaluationResult)
        self.assertEqual(res.num_samples, 4)

        # Assert parameters are strictly identical
        for p_before, p_after in zip(initial_params, model.parameters()):
            self.assertTrue(torch.equal(p_before, p_after))

    def test_14_evaluate_checkpoint_loads_and_evaluates(self) -> None:
        """14. evaluate_checkpoint() loads a synthetic checkpoint and computes metrics."""
        ckpt_path = self.root / "test_model.pth"
        base_model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        torch.save({
            "model_state_dict": base_model.state_dict(),
            "num_classes": NUM_CLASSES,
            "classes": CLASS_NAMES,
            "best_val_accuracy": 0.85,
        }, ckpt_path)

        images = torch.randn(6, 3, 224, 224)
        targets = torch.tensor([0, 1, 2, 3, 4, 5], dtype=torch.int64)
        dataset = TensorDataset(images, targets)
        loader = DataLoader(dataset, batch_size=3, shuffle=False)

        res = evaluate_checkpoint(ckpt_path, loader, device=torch.device("cpu"))
        self.assertIsInstance(res, EvaluationResult)
        self.assertEqual(res.num_samples, 6)
        self.assertEqual(len(res.confusion_matrix), 6)


if __name__ == "__main__":
    unittest.main()
