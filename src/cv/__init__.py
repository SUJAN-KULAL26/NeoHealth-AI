"""NeoHealth AI — Computer Vision and Input Validation Package."""

from src.cv.face_detector import (
    FaceCountStatus,
    FaceDetectionResult,
    MediaPipeFaceDetector,
    evaluate_face_count,
)
from src.cv.quality import ImageQualityResult, compute_quality_metrics
from src.cv.skin_detector import (
    SkinDetectionResult,
    SkinDetectionStatus,
    detect_skin_region,
)
from src.cv.validation import (
    InputValidationStatus,
    ValidationResult,
    validate_input,
)

__all__ = [
    "validate_input",
    "ValidationResult",
    "InputValidationStatus",
    "MediaPipeFaceDetector",
    "FaceDetectionResult",
    "FaceCountStatus",
    "evaluate_face_count",
    "compute_quality_metrics",
    "ImageQualityResult",
    "detect_skin_region",
    "SkinDetectionResult",
    "SkinDetectionStatus",
]
