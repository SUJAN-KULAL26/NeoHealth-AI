"""NeoHealth AI — Input Validation Module.

Validates image inputs prior to computer vision analysis and model inference.
Handles filesystem paths, PIL Images, and NumPy arrays, enforcing supported
formats and verifying image integrity without exposing unhandled exceptions.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image, UnidentifiedImageError

from src.config import SUPPORTED_IMAGE_EXTENSIONS


class InputValidationStatus(str, Enum):
    """Enumeration of input validation statuses."""
    VALID = "VALID"
    INVALID_FORMAT = "INVALID_FORMAT"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_IMAGE = "INVALID_IMAGE"
    UNSUPPORTED_INPUT = "UNSUPPORTED_INPUT"


class ValidationResult:
    """Structured result of input validation."""

    def __init__(
        self,
        status: InputValidationStatus,
        is_valid: bool,
        message: str,
        image_pil: Optional[Image.Image] = None,
        image_np: Optional[np.ndarray] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status = status
        self.is_valid = is_valid
        self.message = message
        self.image_pil = image_pil
        self.image_np = image_np
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result to dictionary (excluding raw image objects)."""
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "message": self.message,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return f"<ValidationResult status={self.status.value} is_valid={self.is_valid}>"


def validate_input(
    input_data: Union[str, Path, Image.Image, np.ndarray],
    supported_extensions: Tuple[str, ...] = tuple(SUPPORTED_IMAGE_EXTENSIONS),
) -> ValidationResult:
    """Validate input format and image data integrity.

    Args:
        input_data: Image as a file path (str or Path), PIL Image, or NumPy array.
        supported_extensions: Tuple of allowed file extensions (case-insensitive).

    Returns:
        ValidationResult containing validation status, converted RGB PIL Image,
        and RGB NumPy array.
    """
    # 1. Path-based input
    if isinstance(input_data, (str, Path)):
        path = Path(input_data)

        # Check file existence
        if not path.exists():
            return ValidationResult(
                status=InputValidationStatus.FILE_NOT_FOUND,
                is_valid=False,
                message=f"File not found: {path}",
                details={"source": str(path)},
            )

        if not path.is_file():
            return ValidationResult(
                status=InputValidationStatus.INVALID_IMAGE,
                is_valid=False,
                message=f"Path is not a regular file: {path}",
                details={"source": str(path)},
            )

        # Check file extension
        suffix = path.suffix.lower()
        if suffix not in supported_extensions:
            return ValidationResult(
                status=InputValidationStatus.INVALID_FORMAT,
                is_valid=False,
                message=(
                    f"Unsupported image extension '{suffix}'. "
                    f"Supported extensions: {sorted(supported_extensions)}"
                ),
                details={"suffix": suffix, "supported": list(supported_extensions)},
            )

        # Attempt to open and verify image integrity
        try:
            with Image.open(path) as img:
                # Force load to catch corrupted/truncated image files
                img.load()
                rgb_pil = img.convert("RGB")
                img_np = np.array(rgb_pil)
                return ValidationResult(
                    status=InputValidationStatus.VALID,
                    is_valid=True,
                    message="Image successfully validated and converted to RGB.",
                    image_pil=rgb_pil,
                    image_np=img_np,
                    details={
                        "source": str(path),
                        "original_format": img.format,
                        "original_size": img.size,
                        "mode": img.mode,
                    },
                )
        except (UnidentifiedImageError, OSError, ValueError) as err:
            return ValidationResult(
                status=InputValidationStatus.INVALID_IMAGE,
                is_valid=False,
                message=f"Failed to decode image file (corrupted or invalid image): {err}",
                details={"source": str(path), "error": str(err)},
            )

    # 2. PIL Image input
    elif isinstance(input_data, Image.Image):
        try:
            input_data.load()
            rgb_pil = input_data.convert("RGB")
            img_np = np.array(rgb_pil)
            return ValidationResult(
                status=InputValidationStatus.VALID,
                is_valid=True,
                message="PIL Image successfully validated and converted to RGB.",
                image_pil=rgb_pil,
                image_np=img_np,
                details={
                    "original_format": getattr(input_data, "format", None),
                    "original_size": input_data.size,
                    "mode": input_data.mode,
                },
            )
        except Exception as err:
            return ValidationResult(
                status=InputValidationStatus.INVALID_IMAGE,
                is_valid=False,
                message=f"Invalid PIL Image: {err}",
                details={"error": str(err)},
            )

    # 3. NumPy array input
    elif isinstance(input_data, np.ndarray):
        # Validate array dimensionality and convert to uint8 RGB
        import cv2

        if input_data.ndim == 2:
            # Grayscale 2D array
            rgb_np = cv2.cvtColor(input_data.astype(np.uint8), cv2.COLOR_GRAY2RGB)
        elif input_data.ndim == 3:
            h, w, c = input_data.shape
            if c == 1:
                rgb_np = cv2.cvtColor(input_data.astype(np.uint8), cv2.COLOR_GRAY2RGB)
            elif c == 3:
                rgb_np = input_data.astype(np.uint8)
            elif c == 4:
                rgb_np = cv2.cvtColor(input_data.astype(np.uint8), cv2.COLOR_RGBA2RGB)
            else:
                return ValidationResult(
                    status=InputValidationStatus.INVALID_IMAGE,
                    is_valid=False,
                    message=f"NumPy array has unsupported channel count: {c}",
                    details={"shape": list(input_data.shape)},
                )
        else:
            return ValidationResult(
                status=InputValidationStatus.INVALID_IMAGE,
                is_valid=False,
                message=f"NumPy array must be 2D or 3D, got {input_data.ndim}D",
                details={"ndim": input_data.ndim},
            )

        rgb_pil = Image.fromarray(rgb_np)
        return ValidationResult(
            status=InputValidationStatus.VALID,
            is_valid=True,
            message="NumPy array successfully validated and converted to RGB.",
            image_pil=rgb_pil,
            image_np=rgb_np,
            details={"original_shape": list(input_data.shape), "dtype": str(input_data.dtype)},
        )

    # 4. Any other unsupported type
    else:
        return ValidationResult(
            status=InputValidationStatus.UNSUPPORTED_INPUT,
            is_valid=False,
            message=f"Unsupported input type '{type(input_data).__name__}'. Expected str, Path, PIL.Image, or np.ndarray.",
            details={"type": type(input_data).__name__},
        )
