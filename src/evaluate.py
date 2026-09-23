"""NeoHealth AI — Model Evaluation Module.

Provides objective, standalone evaluation of trained classification models and
checkpoints using standard medical screening metrics:
- Overall Accuracy
- Precision (macro, weighted, per-class)
- Recall / Sensitivity (macro, weighted, per-class)
- F1-Score (macro, weighted, per-class)
- Support per class
- Six-class Confusion Matrix (6x6)
- One-vs-Rest ROC/AUC (where mathematically applicable)

In accordance with clinical evaluation guidelines:
- Evaluates existing checkpoints in evaluation mode only.
- Never trains or modifies model weights.
- Never fabricates evaluation results or metrics.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)

from src.config import CLASS_NAMES, NUM_CLASSES
from src.inference import load_model


class EvaluationResult:
    """Structured result of classification model evaluation."""

    def __init__(
        self,
        num_samples: int,
        accuracy: float,
        precision: Dict[str, Any],
        recall: Dict[str, Any],
        f1: Dict[str, Any],
        support: Dict[str, int],
        confusion_matrix: List[List[int]],
        roc_auc: Dict[str, Any],
        class_names: Tuple[str, ...] = CLASS_NAMES,
    ) -> None:
        self.num_samples = num_samples
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.support = support
        self.confusion_matrix = confusion_matrix
        self.roc_auc = roc_auc
        self.class_names = class_names

    def to_dict(self) -> Dict[str, Any]:
        """Serialize evaluation result to dictionary."""
        return {
            "num_samples": self.num_samples,
            "accuracy": round(self.accuracy, 6),
            "precision": {
                "macro": round(self.precision["macro"], 6),
                "weighted": round(self.precision["weighted"], 6),
                "per_class": {
                    cls: round(score, 6)
                    for cls, score in self.precision["per_class"].items()
                },
            },
            "recall": {
                "macro": round(self.recall["macro"], 6),
                "weighted": round(self.recall["weighted"], 6),
                "per_class": {
                    cls: round(score, 6)
                    for cls, score in self.recall["per_class"].items()
                },
            },
            "f1": {
                "macro": round(self.f1["macro"], 6),
                "weighted": round(self.f1["weighted"], 6),
                "per_class": {
                    cls: round(score, 6)
                    for cls, score in self.f1["per_class"].items()
                },
            },
            "support": self.support,
            "confusion_matrix": self.confusion_matrix,
            "roc_auc": self.roc_auc,
        }

    def __repr__(self) -> str:
        return (
            f"<EvaluationResult samples={self.num_samples} "
            f"acc={self.accuracy:.4f} f1_macro={self.f1['macro']:.4f}>"
        )


def _convert_labels_to_indices(
    labels: Sequence[Union[int, str]],
    class_names: Tuple[str, ...],
) -> np.ndarray:
    """Convert label sequence (ints or class name strings) to integer indices."""
    class_to_idx = {name: i for i, name in enumerate(class_names)}
    indices: List[int] = []

    for item in labels:
        if isinstance(item, (int, np.integer)):
            idx = int(item)
            if idx < 0 or idx >= len(class_names):
                raise ValueError(
                    f"Label index {idx} out of range [0, {len(class_names) - 1}]."
                )
            indices.append(idx)
        elif isinstance(item, str):
            if item not in class_to_idx:
                raise ValueError(
                    f"Label '{item}' is not one of the canonical classes: {class_names}."
                )
            indices.append(class_to_idx[item])
        else:
            raise TypeError(
                f"Unsupported label element type '{type(item).__name__}'. Expected int or str."
            )

    return np.array(indices, dtype=np.int64)


def compute_metrics(
    y_true: Sequence[Union[int, str]],
    y_pred: Sequence[Union[int, str]],
    y_probs: Optional[Union[np.ndarray, torch.Tensor, Sequence[Sequence[float]]]] = None,
    class_names: Tuple[str, ...] = CLASS_NAMES,
) -> EvaluationResult:
    """Calculate comprehensive classification metrics for medical screening.

    Args:
        y_true: Sequence of ground truth class indices or names.
        y_pred: Sequence of predicted class indices or names.
        y_probs: Optional (N, num_classes) array of predicted class probabilities.
        class_names: Canonical ordered class names (defaults to config.CLASS_NAMES).

    Returns:
        EvaluationResult containing accuracy, precision, recall, F1, support,
        confusion matrix, and ROC/AUC (where applicable).

    Raises:
        ValueError: If input lengths mismatch, inputs are empty, or probabilities
                    have invalid dimensions.
    """
    if len(y_true) == 0 or len(y_pred) == 0:
        raise ValueError("Cannot compute evaluation metrics on empty input sequences.")

    if len(y_true) != len(y_pred):
        raise ValueError(
            f"Length mismatch: y_true ({len(y_true)}) != y_pred ({len(y_pred)})."
        )

    num_samples = len(y_true)
    num_classes = len(class_names)
    labels_order = list(range(num_classes))

    # Convert to standard int arrays
    targets = _convert_labels_to_indices(y_true, class_names)
    predictions = _convert_labels_to_indices(y_pred, class_names)

    # 1. Overall Accuracy
    acc = float(accuracy_score(targets, predictions))

    # 2. Per-class metrics and support
    per_class_p, per_class_r, per_class_f1, per_class_supp = (
        precision_recall_fscore_support(
            targets,
            predictions,
            labels=labels_order,
            zero_division=0,
        )
    )

    # 3. Macro and Weighted metrics
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        targets,
        predictions,
        labels=labels_order,
        average="macro",
        zero_division=0,
    )

    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        targets,
        predictions,
        labels=labels_order,
        average="weighted",
        zero_division=0,
    )

    precision_dict = {
        "macro": float(macro_p),
        "weighted": float(weighted_p),
        "per_class": {
            class_names[i]: float(per_class_p[i]) for i in range(num_classes)
        },
    }

    recall_dict = {
        "macro": float(macro_r),
        "weighted": float(weighted_r),
        "per_class": {
            class_names[i]: float(per_class_r[i]) for i in range(num_classes)
        },
    }

    f1_dict = {
        "macro": float(macro_f1),
        "weighted": float(weighted_f1),
        "per_class": {
            class_names[i]: float(per_class_f1[i]) for i in range(num_classes)
        },
    }

    support_dict = {
        class_names[i]: int(per_class_supp[i]) for i in range(num_classes)
    }

    # 4. Confusion Matrix (strictly 6x6 matching class_names order)
    cm = confusion_matrix(targets, predictions, labels=labels_order)
    confusion_matrix_list: List[List[int]] = cm.tolist()

    # 5. ROC / AUC calculation
    roc_auc_result: Dict[str, Any] = {
        "available": False,
        "macro": None,
        "per_class": {name: None for name in class_names},
        "message": "Probabilities were not provided.",
    }

    if y_probs is not None:
        if isinstance(y_probs, torch.Tensor):
            probs_arr = y_probs.detach().cpu().numpy()
        elif isinstance(y_probs, np.ndarray):
            probs_arr = y_probs
        else:
            probs_arr = np.array(y_probs, dtype=np.float64)

        if probs_arr.ndim != 2:
            raise ValueError(
                f"Invalid probability dimensions: expected 2D array, got {probs_arr.ndim}D."
            )

        if probs_arr.shape[0] != num_samples:
            raise ValueError(
                f"Sample count mismatch: y_probs has {probs_arr.shape[0]} rows, "
                f"expected {num_samples} to match y_true."
            )

        if probs_arr.shape[1] != num_classes:
            raise ValueError(
                f"Class count mismatch: y_probs has {probs_arr.shape[1]} columns, "
                f"expected {num_classes} matching class_names."
            )

        per_class_auc: Dict[str, Optional[float]] = {}
        valid_auc_scores: List[float] = []
        unavailable_classes: List[str] = []

        for i, name in enumerate(class_names):
            binary_targets = (targets == i).astype(int)
            positives = int(np.sum(binary_targets))
            negatives = num_samples - positives

            # AUC requires at least one positive and at least one negative sample
            if positives > 0 and negatives > 0:
                try:
                    score = float(roc_auc_score(binary_targets, probs_arr[:, i]))
                    per_class_auc[name] = round(score, 6)
                    valid_auc_scores.append(score)
                except Exception:
                    per_class_auc[name] = None
                    unavailable_classes.append(name)
            else:
                per_class_auc[name] = None
                unavailable_classes.append(name)

        if len(valid_auc_scores) == num_classes:
            macro_auc = float(np.mean(valid_auc_scores))
            roc_auc_result = {
                "available": True,
                "macro": round(macro_auc, 6),
                "per_class": per_class_auc,
                "message": "Multiclass one-vs-rest ROC/AUC successfully computed for all classes.",
            }
        else:
            roc_auc_result = {
                "available": False,
                "macro": None,
                "per_class": per_class_auc,
                "message": (
                    f"ROC/AUC unavailable for classes without positive/negative samples: "
                    f"{unavailable_classes}."
                ),
            }

    return EvaluationResult(
        num_samples=num_samples,
        accuracy=acc,
        precision=precision_dict,
        recall=recall_dict,
        f1=f1_dict,
        support=support_dict,
        confusion_matrix=confusion_matrix_list,
        roc_auc=roc_auc_result,
        class_names=class_names,
    )


def evaluate_model(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: Optional[torch.device] = None,
    class_names: Tuple[str, ...] = CLASS_NAMES,
) -> EvaluationResult:
    """Evaluate an instantiated PyTorch model on a DataLoader without modifying weights.

    Args:
        model: PyTorch model instance (set to eval mode).
        dataloader: DataLoader yielding (images, targets) batches.
        device: PyTorch device (CUDA or CPU). If None, auto-detected from model.
        class_names: Canonical class names.

    Returns:
        EvaluationResult containing comprehensive evaluation metrics.
    """
    if device is None:
        try:
            device = next(model.parameters()).device
        except (StopIteration, AttributeError):
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.eval()

    all_targets: List[int] = []
    all_preds: List[int] = []
    all_probs: List[np.ndarray] = []

    with torch.no_grad():
        for batch in dataloader:
            if isinstance(batch, (list, tuple)):
                images, targets = batch[0], batch[1]
            else:
                raise TypeError(
                    f"Expected DataLoader batch to be a tuple/list of (images, targets), got {type(batch)}."
                )

            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            all_targets.extend(targets.cpu().numpy().tolist())
            all_preds.extend(preds.cpu().numpy().tolist())
            all_probs.append(probs.cpu().numpy())

    y_probs = np.concatenate(all_probs, axis=0) if all_probs else None

    return compute_metrics(
        y_true=all_targets,
        y_pred=all_preds,
        y_probs=y_probs,
        class_names=class_names,
    )


def evaluate_checkpoint(
    checkpoint_path: Union[str, Path],
    dataloader: DataLoader,
    device: Optional[torch.device] = None,
    class_names: Tuple[str, ...] = CLASS_NAMES,
) -> EvaluationResult:
    """Load a model checkpoint and evaluate it on a DataLoader without retraining.

    Args:
        checkpoint_path: Path to the .pth model checkpoint.
        dataloader: DataLoader yielding evaluation samples.
        device: Target execution device.
        class_names: Canonical class names.

    Returns:
        EvaluationResult containing comprehensive evaluation metrics.
    """
    model, resolved_device = load_model(checkpoint_path, device=device)
    return evaluate_model(
        model=model,
        dataloader=dataloader,
        device=resolved_device,
        class_names=class_names,
    )


__all__ = [
    "EvaluationResult",
    "compute_metrics",
    "evaluate_model",
    "evaluate_checkpoint",
]
