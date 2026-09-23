"""NeoHealth AI - Six-class EfficientNet-B0 inference."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image
import torch

from src.config import CLASS_NAMES, DISCLAIMER_TEXT, NUM_CLASSES
from src.cv import (
    FaceCountStatus,
    MediaPipeFaceDetector,
    compute_quality_metrics,
    detect_skin_region,
    validate_input,
)
from src.data.preprocessing import get_inference_transforms
from src.models.efficientnet import create_efficientnet_b0


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "efficientnet_b0_best.pth"
)

# Initial engineering threshold.
# This is NOT a clinically validated threshold.
CONFIDENCE_THRESHOLD = 0.70


def load_model(
    model_path: Union[str, Path] = MODEL_PATH,
    device: Optional[torch.device] = None,
) -> Tuple[torch.nn.Module, torch.device]:
    """Load and validate the canonical six-class EfficientNet-B0 checkpoint.

    Args:
        model_path: Path to the .pth checkpoint file. Defaults to MODEL_PATH.
        device: PyTorch device (CPU or CUDA). If None, selects CUDA if available, else CPU.

    Returns:
        Tuple of (model, device) with the model configured in evaluation mode.

    Raises:
        FileNotFoundError: If model_path does not exist or is not a regular file.
        ValueError: If checkpoint format or metadata is invalid or inconsistent with canonical configuration.
        RuntimeError: If checkpoint file cannot be read or state dict fails to load.
    """
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model checkpoint not found at '{path}'. "
            f"Please ensure the trained EfficientNet-B0 checkpoint is provisioned."
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"Model checkpoint path '{path}' is not a regular file."
        )

    if device is None:
        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    try:
        checkpoint = torch.load(
            path,
            map_location=device,
        )
    except Exception as err:
        raise RuntimeError(
            f"Failed to load checkpoint file from '{path}': {err}"
        ) from err

    if not isinstance(checkpoint, dict):
        raise ValueError(
            f"Invalid checkpoint format in '{path}': expected a dictionary, got {type(checkpoint).__name__}."
        )

    if "model_state_dict" not in checkpoint:
        raise ValueError(
            f"Invalid checkpoint in '{path}': missing required key 'model_state_dict'."
        )

    if "num_classes" in checkpoint:
        if checkpoint["num_classes"] != NUM_CLASSES:
            raise ValueError(
                f"Checkpoint num_classes mismatch: expected {NUM_CLASSES}, got {checkpoint['num_classes']}."
            )
    else:
        raise ValueError(
            f"Invalid checkpoint in '{path}': missing required key 'num_classes'."
        )

    if "classes" in checkpoint:
        ckpt_classes = tuple(checkpoint["classes"])
        if ckpt_classes != CLASS_NAMES:
            raise ValueError(
                f"Checkpoint classes mismatch: expected {CLASS_NAMES}, got {ckpt_classes}."
            )
    else:
        raise ValueError(
            f"Invalid checkpoint in '{path}': missing required key 'classes'."
        )

    model = create_efficientnet_b0(
        num_classes=NUM_CLASSES,
        pretrained=False,
    )

    try:
        model.load_state_dict(checkpoint["model_state_dict"])
    except Exception as err:
        raise RuntimeError(
            f"Failed to load model state_dict from '{path}': {err}"
        ) from err

    model.to(device)
    model.eval()

    return model, device


def predict_image(
    image: Union[str, Path, Image.Image, np.ndarray],
    model: Optional[Any] = None,
    device: Optional[torch.device] = None,
    face_detector: Optional[Any] = None,
    model_path: Optional[Union[str, Path]] = None,
) -> Dict[str, object]:
    """Run six-class prediction with CV gatekeeping and confidence-aware screening.

    Pipeline:
        1. Format & Integrity Validation (str, Path, PIL.Image, or np.ndarray)
        2. Face Detection & Exactly-One-Face Validation (MediaPipe Tasks FaceDetector)
        3. Image Quality Metrics (sharpness, brightness, contrast)
        4. Skin Region Detection (YCrCb + HSV color segmentation)
        5. Locked 5-Stage Preprocessing (Resize, White Balance, Color Norm, Noise Removal, Tensor Prep)
        6. EfficientNet-B0 Screening Prediction & Confidence Evaluation

    Args:
        image: Input image as a filesystem path, PIL Image, or NumPy array.
        model: Loaded EfficientNet-B0 model in eval mode. If None, auto-resolved via load_model().
        device: PyTorch device (CPU or CUDA). If None, auto-resolved.
        face_detector: Optional initialized FaceDetector instance (for testing or injection).
        model_path: Optional path to model checkpoint if model is auto-resolved. Defaults to MODEL_PATH.

    Returns:
        Structured result dictionary. If any hard gate fails or model loading fails, returns
        validation failure details without invoking model inference. Always includes medical disclaimer.
    """
    # --------------------------------------------------------------------------
    # GATE 1: Input Format & Integrity Validation
    # --------------------------------------------------------------------------
    val_result = validate_input(image)
    if not val_result.is_valid:
        return {
            "status": val_result.status.value,
            "is_valid": False,
            "validation_passed": False,
            "message": val_result.message,
            "validation_details": {
                "format": val_result.to_dict(),
            },
            "disclaimer": DISCLAIMER_TEXT,
        }

    # --------------------------------------------------------------------------
    # GATE 2: Face Detection & Exactly-One-Face Check
    # --------------------------------------------------------------------------
    detector = face_detector
    if detector is None:
        try:
            detector = MediaPipeFaceDetector()
        except FileNotFoundError as err:
            return {
                "status": "FACE_DETECTOR_MODEL_MISSING",
                "is_valid": False,
                "validation_passed": False,
                "message": str(err),
                "validation_details": {
                    "format": val_result.to_dict(),
                },
                "disclaimer": DISCLAIMER_TEXT,
            }

    face_result = detector.detect(val_result.image_np)
    if face_result.status != FaceCountStatus.EXACTLY_ONE_FACE:
        return {
            "status": face_result.status.value,
            "is_valid": False,
            "validation_passed": False,
            "message": face_result.message,
            "validation_details": {
                "format": val_result.to_dict(),
                "face_detection": face_result.to_dict(),
            },
            "disclaimer": DISCLAIMER_TEXT,
        }

    # --------------------------------------------------------------------------
    # GATE 3: Image Quality Metrics (Reported; unassessed without clinical thresholds)
    # --------------------------------------------------------------------------
    quality_result = compute_quality_metrics(val_result.image_np)

    # --------------------------------------------------------------------------
    # GATE 4: Skin Region Detection
    # --------------------------------------------------------------------------
    skin_result = detect_skin_region(val_result.image_np)
    if not skin_result.has_skin:
        return {
            "status": skin_result.status.value,
            "is_valid": False,
            "validation_passed": False,
            "message": skin_result.message,
            "validation_details": {
                "format": val_result.to_dict(),
                "face_detection": face_result.to_dict(),
                "quality": quality_result.to_dict(),
                "skin_detection": skin_result.to_dict(),
            },
            "disclaimer": DISCLAIMER_TEXT,
        }

    # --------------------------------------------------------------------------
    # MODEL RESOLUTION: Auto-load if not provided
    # --------------------------------------------------------------------------
    if model is None:
        target_path = model_path if model_path is not None else MODEL_PATH
        try:
            model, resolved_device = load_model(model_path=target_path, device=device)
            device = resolved_device
        except FileNotFoundError as err:
            return {
                "status": "MODEL_NOT_FOUND",
                "is_valid": False,
                "validation_passed": False,
                "message": str(err),
                "validation_details": {
                    "format": val_result.to_dict(),
                    "face_detection": face_result.to_dict(),
                    "quality": quality_result.to_dict(),
                    "skin_detection": skin_result.to_dict(),
                },
                "disclaimer": DISCLAIMER_TEXT,
            }
        except (ValueError, RuntimeError, Exception) as err:
            return {
                "status": "MODEL_LOAD_FAILED",
                "is_valid": False,
                "validation_passed": False,
                "message": str(err),
                "validation_details": {
                    "format": val_result.to_dict(),
                    "face_detection": face_result.to_dict(),
                    "quality": quality_result.to_dict(),
                    "skin_detection": skin_result.to_dict(),
                },
                "disclaimer": DISCLAIMER_TEXT,
            }
    else:
        if device is None:
            try:
                device = next(model.parameters()).device
            except (StopIteration, AttributeError):
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # --------------------------------------------------------------------------
    # GATE 5: Preprocessing & Model Inference
    # --------------------------------------------------------------------------
    transform = get_inference_transforms()
    tensor = transform(val_result.image_pil).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)

    confidence, predicted_index = torch.max(
        probabilities,
        dim=1,
    )

    predicted_index = int(predicted_index.item())
    confidence = float(confidence.item())

    probability_dict = {
        class_name: float(
            probabilities[0, index].item()
        )
        for index, class_name in enumerate(CLASS_NAMES)
    }

    is_confident = confidence >= CONFIDENCE_THRESHOLD

    return {
        "prediction": CLASS_NAMES[predicted_index],
        "confidence": confidence,
        "confidence_percent": confidence * 100.0,
        "is_confident": is_confident,
        "status": (
            "screening_result"
            if is_confident
            else "uncertain_review_required"
        ),
        "probabilities": probability_dict,
        "validation_details": {
            "format": val_result.to_dict(),
            "face_detection": face_result.to_dict(),
            "quality": quality_result.to_dict(),
            "skin_detection": skin_result.to_dict(),
        },
        "disclaimer": DISCLAIMER_TEXT,
    }