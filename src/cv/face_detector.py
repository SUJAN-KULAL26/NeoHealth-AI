"""NeoHealth AI — Face Detection Module.

Implements face detection and exactly-one-face validation using the MediaPipe
Tasks FaceDetector API. Rejects screening inputs that contain zero faces or
multiple faces, ensuring clinical screening is strictly restricted to a single
infant subject.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
from PIL import Image

from src.config import FACE_DETECTOR_MODEL_PATH


class FaceCountStatus(str, Enum):
    """Enumeration of face count gatekeeper statuses."""
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    EXACTLY_ONE_FACE = "EXACTLY_ONE_FACE"
    MULTIPLE_FACES_DETECTED = "MULTIPLE_FACES_DETECTED"


def evaluate_face_count(count: int) -> FaceCountStatus:
    """Pure decision logic for the clinical single-subject gatekeeper.

    Args:
        count: Number of faces detected in the image.

    Returns:
        FaceCountStatus indicating NO_FACE_DETECTED, EXACTLY_ONE_FACE,
        or MULTIPLE_FACES_DETECTED.
    """
    if count == 0:
        return FaceCountStatus.NO_FACE_DETECTED
    elif count == 1:
        return FaceCountStatus.EXACTLY_ONE_FACE
    else:
        return FaceCountStatus.MULTIPLE_FACES_DETECTED


class FaceDetectionResult:
    """Structured result of face detection analysis."""

    def __init__(
        self,
        status: FaceCountStatus,
        is_valid: bool,
        face_count: int,
        boxes: List[Dict[str, Any]],
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status = status
        self.is_valid = is_valid
        self.face_count = face_count
        self.boxes = boxes
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "face_count": self.face_count,
            "boxes": self.boxes,
            "message": self.message,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return (
            f"<FaceDetectionResult status={self.status.value} "
            f"count={self.face_count} is_valid={self.is_valid}>"
        )


class MediaPipeFaceDetector:
    """MediaPipe Tasks Face Detector wrapper.

    Detects faces in RGB images using the MediaPipe Tasks FaceDetector API.
    Enforces the project-wide single-subject screening gatekeeper.
    """

    def __init__(
        self,
        model_asset_path: Optional[Union[str, Path]] = None,
        min_detection_confidence: float = 0.5,
    ) -> None:
        """Initialize the MediaPipe Tasks Face Detector.

        Args:
            model_asset_path: Path to the MediaPipe face detector .tflite model.
                              Defaults to config.FACE_DETECTOR_MODEL_PATH.
            min_detection_confidence: Minimum confidence score for face detection.

        Raises:
            FileNotFoundError: If the model asset file is missing from disk.
        """
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions, vision

        self.model_path = (
            Path(model_asset_path)
            if model_asset_path is not None
            else FACE_DETECTOR_MODEL_PATH
        )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"MediaPipe FaceDetector model asset not found at '{self.model_path}'. "
                f"Please provision 'blaze_face_short_range.tflite' in the models/ directory."
            )

        base_options = BaseOptions(model_asset_path=str(self.model_path))
        options = vision.FaceDetectorOptions(
            base_options=base_options,
            min_detection_confidence=min_detection_confidence,
        )
        self._detector = vision.FaceDetector.create_from_options(options)

    def detect(
        self,
        image: Union[np.ndarray, Image.Image],
    ) -> FaceDetectionResult:
        """Detect faces in an RGB image.

        Args:
            image: RGB image as a NumPy uint8 array or PIL Image.

        Returns:
            FaceDetectionResult containing count, bounding boxes, and gatekeeper status.
        """
        import mediapipe as mp

        if isinstance(image, Image.Image):
            rgb_np = np.array(image.convert("RGB"), dtype=np.uint8)
        elif isinstance(image, np.ndarray):
            rgb_np = image.astype(np.uint8)
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_np)
        detection_result = self._detector.detect(mp_image)

        boxes: List[Dict[str, Any]] = []
        for detection in detection_result.detections:
            bbox = detection.bounding_box
            score = (
                float(detection.categories[0].score)
                if detection.categories
                else 1.0
            )
            boxes.append({
                "origin_x": int(bbox.origin_x),
                "origin_y": int(bbox.origin_y),
                "width": int(bbox.width),
                "height": int(bbox.height),
                "score": score,
            })

        face_count = len(boxes)
        status = evaluate_face_count(face_count)
        is_valid = status == FaceCountStatus.EXACTLY_ONE_FACE

        if status == FaceCountStatus.NO_FACE_DETECTED:
            message = "No face detected in the image. Infant face must be clearly visible."
        elif status == FaceCountStatus.EXACTLY_ONE_FACE:
            message = "Exactly one infant face detected. Screening validation passed."
        else:
            message = (
                f"Multiple faces ({face_count}) detected. "
                f"Screening must focus on exactly one infant subject."
            )

        return FaceDetectionResult(
            status=status,
            is_valid=is_valid,
            face_count=face_count,
            boxes=boxes,
            message=message,
            details={"detector": "MediaPipe_Tasks_FaceDetector"},
        )
