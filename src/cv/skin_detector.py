"""NeoHealth AI — Skin Region Detection Module.

Implements dermatological skin tissue isolation using YCrCb and HSV color space
segmentation combined with morphological filtering. Identifies cutaneous regions
of interest without imposing arbitrary clinical coverage thresholds.
"""

from enum import Enum
from typing import Any, Dict, Optional, Union

import cv2
import numpy as np
from PIL import Image


class SkinDetectionStatus(str, Enum):
    """Enumeration of skin detection statuses."""
    SKIN_REGION_DETECTED = "SKIN_REGION_DETECTED"
    SKIN_REGION_UNAVAILABLE = "SKIN_REGION_UNAVAILABLE"


class SkinDetectionResult:
    """Structured result of skin region detection and segmentation."""

    def __init__(
        self,
        status: SkinDetectionStatus,
        has_skin: bool,
        skin_pixels: int,
        total_pixels: int,
        coverage_ratio: float,
        bounding_box: Optional[Dict[str, int]],
        mask: np.ndarray,
        message: str,
    ) -> None:
        self.status = status
        self.has_skin = has_skin
        self.skin_pixels = skin_pixels
        self.total_pixels = total_pixels
        self.coverage_ratio = coverage_ratio
        self.bounding_box = bounding_box
        self.mask = mask
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary (excluding binary mask array)."""
        return {
            "status": self.status.value,
            "has_skin": self.has_skin,
            "skin_pixels": self.skin_pixels,
            "total_pixels": self.total_pixels,
            "coverage_ratio": round(self.coverage_ratio, 4),
            "bounding_box": self.bounding_box,
            "message": self.message,
        }

    def __repr__(self) -> str:
        return (
            f"<SkinDetectionResult status={self.status.value} "
            f"has_skin={self.has_skin} coverage={self.coverage_ratio:.2%}>"
        )


def detect_skin_region(
    image: Union[np.ndarray, Image.Image],
) -> SkinDetectionResult:
    """Detect and segment skin regions using dual YCrCb and HSV color spaces.

    The algorithm computes:
    1. YCrCb chroma bounds: Cr in [133, 173], Cb in [77, 127]
    2. HSV bounds: H in [0, 50], S in [30, 200], V in [60, 255]
    3. Intersection mask: Bitwise-AND of YCrCb and HSV candidate masks
    4. Morphological filtering: Elliptical opening and closing to suppress noise
    5. Cutaneous metrics: Pixel count, coverage ratio, and bounding box

    Note:
        Does NOT apply an arbitrary heuristic percentage threshold to decide
        whether coverage is clinically 'adequate'. If zero cutaneous pixels
        are identified, status is set to SKIN_REGION_UNAVAILABLE.

    Args:
        image: RGB image as a NumPy uint8 array or PIL Image.

    Returns:
        SkinDetectionResult with binary mask, bounding coordinates, and metrics.
    """
    if isinstance(image, Image.Image):
        rgb_np = np.array(image.convert("RGB"), dtype=np.uint8)
    elif isinstance(image, np.ndarray):
        if image.ndim == 2:
            rgb_np = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        elif image.ndim == 3 and image.shape[2] == 4:
            rgb_np = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGBA2RGB)
        else:
            rgb_np = image.astype(np.uint8)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")

    total_pixels = int(rgb_np.shape[0] * rgb_np.shape[1])

    # 1. YCrCb Segmentation
    ycrcb = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2YCrCb)
    lower_ycrcb = np.array([0, 133, 77], dtype=np.uint8)
    upper_ycrcb = np.array([255, 173, 127], dtype=np.uint8)
    mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)

    # 2. HSV Segmentation
    hsv = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2HSV)
    lower_hsv = np.array([0, 30, 60], dtype=np.uint8)
    upper_hsv = np.array([50, 200, 255], dtype=np.uint8)
    mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)

    # 3. Intersect masks to eliminate background false positives
    combined_mask = cv2.bitwise_and(mask_ycrcb, mask_hsv)

    # 4. Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    skin_pixels = int(np.count_nonzero(cleaned_mask))
    coverage_ratio = float(skin_pixels / total_pixels) if total_pixels > 0 else 0.0

    if skin_pixels > 0:
        y_indices, x_indices = np.nonzero(cleaned_mask)
        min_x = int(np.min(x_indices))
        max_x = int(np.max(x_indices))
        min_y = int(np.min(y_indices))
        max_y = int(np.max(y_indices))

        bounding_box = {
            "x": min_x,
            "y": min_y,
            "width": max_x - min_x + 1,
            "height": max_y - min_y + 1,
        }
        status = SkinDetectionStatus.SKIN_REGION_DETECTED
        has_skin = True
        message = (
            f"Skin region detected ({skin_pixels} pixels, "
            f"{coverage_ratio:.2%} coverage)."
        )
    else:
        bounding_box = None
        status = SkinDetectionStatus.SKIN_REGION_UNAVAILABLE
        has_skin = False
        message = "No cutaneous skin region detected in the image."

    return SkinDetectionResult(
        status=status,
        has_skin=has_skin,
        skin_pixels=skin_pixels,
        total_pixels=total_pixels,
        coverage_ratio=coverage_ratio,
        bounding_box=bounding_box,
        mask=cleaned_mask,
        message=message,
    )
