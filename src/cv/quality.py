"""NeoHealth AI — Image Quality Assessment Module.

Computes objective computer vision metrics for image quality (sharpness,
brightness, contrast, and dimensions) without imposing arbitrary clinical
thresholds. Clinical acceptance criteria must be determined through formal
experimental validation on pediatric datasets.
"""

from typing import Any, Dict, Union

import cv2
import numpy as np
from PIL import Image


class ImageQualityResult:
    """Structured result of image quality metric computation."""

    def __init__(
        self,
        status: str,
        is_assessed: bool,
        metrics: Dict[str, float],
        message: str,
    ) -> None:
        self.status = status
        self.is_assessed = is_assessed
        self.metrics = metrics
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary."""
        return {
            "status": self.status,
            "is_assessed": self.is_assessed,
            "metrics": self.metrics,
            "message": self.message,
        }

    def __repr__(self) -> str:
        return f"<ImageQualityResult status={self.status} is_assessed={self.is_assessed}>"


def compute_quality_metrics(
    image: Union[np.ndarray, Image.Image],
) -> ImageQualityResult:
    """Compute objective image quality metrics on an input image.

    Calculates:
    - Laplacian variance: Quantifies high-frequency edge content (sharpness vs. blur).
    - Mean brightness: Average intensity of the grayscale representation.
    - Contrast: Standard deviation of pixel intensities across the scene.
    - Intensity range: Minimum and maximum intensity values.
    - Spatial dimensions: Height, width, and color channels.

    Note:
        In adherence to clinical safety guidelines, this module does NOT reject
        images using arbitrary heuristic thresholds. Metrics are reported
        objectively for downstream clinical calibration.

    Args:
        image: Input image as a NumPy uint8 array or PIL Image.

    Returns:
        ImageQualityResult containing raw calculated metrics.
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

    height, width = rgb_np.shape[:2]
    channels = rgb_np.shape[2] if rgb_np.ndim == 3 else 1

    # Convert to grayscale for luminance analysis
    gray = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2GRAY)

    # 1. Sharpness via Laplacian variance
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # 2. Photometric distribution
    mean_brightness = float(np.mean(gray))
    contrast_std = float(np.std(gray))
    min_brightness = float(np.min(gray))
    max_brightness = float(np.max(gray))

    metrics: Dict[str, float] = {
        "width": float(width),
        "height": float(height),
        "channels": float(channels),
        "sharpness_laplacian_var": laplacian_var,
        "mean_brightness": mean_brightness,
        "contrast_std": contrast_std,
        "min_brightness": min_brightness,
        "max_brightness": max_brightness,
    }

    return ImageQualityResult(
        status="quality_unassessed",
        is_assessed=False,
        metrics=metrics,
        message="Image quality metrics calculated; clinical assessment requires experimentally established thresholds.",
    )
