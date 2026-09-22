"""NeoHealth AI — Image Preprocessing Module.

Implements the five locked preprocessing stages in strict conceptual sequence:
1. Resize: Rescales input image to IMAGE_SIZE (224, 224).
2. White Balance: Gray World algorithm to mitigate ambient lighting variations.
3. Color Normalization: Dynamic range standardization into normalized float space [0.0, 1.0].
4. Noise Removal: Gentle Gaussian smoothing to attenuate acquisition sensor noise while
   preserving lesion margins and diagnostic edges.
5. Tensor Preparation: Conversion from HWC NumPy array to CHW PyTorch float32 tensor
   of shape [3, 224, 224], followed by ImageNet mean/std standardization for compatibility
   with the ImageNet-pretrained backbone.

Note: Color Normalization (Stage 3) and ImageNet Standardization (Stage 5) are
conceptually distinct operations. Color normalization operates in image color space,
whereas ImageNet standardization adapts the tensor to the feature distribution expected
by the pretrained convolutional backbone.
"""

from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms

from src.config import IMAGE_SIZE

# ImageNet statistics for transfer learning tensor preparation
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)


# ==============================================================================
# STAGE 1: RESIZE
# ==============================================================================

def resize_image(image: Image.Image, size: Tuple[int, int] = IMAGE_SIZE) -> Image.Image:
    """Stage 1: Resize image to target dimensions.

    Args:
        image: Input PIL Image (expected RGB).
        size: Target (width, height) tuple, defaulting to config.IMAGE_SIZE (224, 224).

    Returns:
        Resized PIL Image.
    """
    if image.size == size:
        return image
    return image.resize(size, resample=Image.Resampling.BILINEAR)


# ==============================================================================
# STAGE 2: WHITE BALANCE (GRAY WORLD ALGORITHM)
# ==============================================================================

def white_balance_gray_world(img_np: np.ndarray) -> np.ndarray:
    """Stage 2: White Balance using the Gray World assumption.

    Under the Gray World assumption, the average reflected color in a scene is
    neutral gray. This algorithm computes the mean intensity of each RGB channel,
    calculates an overall gray reference mean, and scales each channel accordingly.

    Args:
        img_np: RGB image as uint8 or float32 NumPy array with shape (H, W, 3).

    Returns:
        White-balanced image as float32 NumPy array with shape (H, W, 3) in range [0, 255].
    """
    img_float = img_np.astype(np.float32)

    # Compute mean for each color channel
    mean_r = np.mean(img_float[:, :, 0])
    mean_g = np.mean(img_float[:, :, 1])
    mean_b = np.mean(img_float[:, :, 2])

    gray_ref = (mean_r + mean_g + mean_b) / 3.0

    # Scale channels, guarding against division by zero
    scale_r = (gray_ref / mean_r) if mean_r > 1e-6 else 1.0
    scale_g = (gray_ref / mean_g) if mean_g > 1e-6 else 1.0
    scale_b = (gray_ref / mean_b) if mean_b > 1e-6 else 1.0

    balanced = np.empty_like(img_float)
    balanced[:, :, 0] = np.clip(img_float[:, :, 0] * scale_r, 0.0, 255.0)
    balanced[:, :, 1] = np.clip(img_float[:, :, 1] * scale_g, 0.0, 255.0)
    balanced[:, :, 2] = np.clip(img_float[:, :, 2] * scale_b, 0.0, 255.0)

    return balanced


# ==============================================================================
# STAGE 3: COLOR NORMALIZATION
# ==============================================================================

def color_normalize(img_np: np.ndarray) -> np.ndarray:
    """Stage 3: Color Normalization into standardized [0.0, 1.0] range.

    Standardizes image color dynamic range into continuous floating point space [0.0, 1.0].
    This is distinct from ImageNet mean/std standardization, which is performed
    subsequently during tensor preparation.

    Args:
        img_np: RGB image as NumPy array with shape (H, W, 3), values in [0, 255].

    Returns:
        Color-normalized float32 NumPy array with shape (H, W, 3) and values in [0.0, 1.0].
    """
    img_float = img_np.astype(np.float32)
    normalized = img_float / 255.0
    return np.clip(normalized, 0.0, 1.0)


# ==============================================================================
# STAGE 4: NOISE REMOVAL
# ==============================================================================

def noise_removal(
    img_np: np.ndarray,
    kernel_size: int = 3,
    sigma: float = 0.5,
) -> np.ndarray:
    """Stage 4: Noise Removal via gentle Gaussian smoothing.

    Attenuates sensor noise and digital acquisition artifacts while preserving
    lesion boundaries and dermatological textures.

    Args:
        img_np: RGB float32 array in [0.0, 1.0] or uint8 array with shape (H, W, 3).
        kernel_size: Size of Gaussian blur kernel (must be odd positive integer, default 3).
        sigma: Standard deviation of Gaussian blur kernel (default 0.5 for mild smoothing).

    Returns:
        Denoised float32 NumPy array with shape (H, W, 3) in range [0.0, 1.0].
    """
    if kernel_size % 2 == 0:
        kernel_size += 1

    denoised = cv2.GaussianBlur(
        img_np.astype(np.float32),
        (kernel_size, kernel_size),
        sigmaX=sigma,
        sigmaY=sigma,
    )
    return np.clip(denoised, 0.0, 1.0)


# ==============================================================================
# STAGE 5: TENSOR PREPARATION
# ==============================================================================

def prepare_tensor(
    img_np: np.ndarray,
    apply_imagenet_norm: bool = True,
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD,
) -> torch.Tensor:
    """Stage 5: Tensor Preparation and ImageNet Backbone Standardization.

    Converts an HWC RGB float32 NumPy array into a CHW PyTorch tensor with
    shape [3, H, W] and dtype float32. When apply_imagenet_norm is True,
    standardizes the tensor with ImageNet mean and std for transfer learning.

    Args:
        img_np: RGB float32 NumPy array with shape (H, W, 3), values in [0.0, 1.0].
        apply_imagenet_norm: Whether to apply ImageNet mean and std standardization.
        mean: Normalization mean per channel (default ImageNet).
        std: Normalization standard deviation per channel (default ImageNet).

    Returns:
        PyTorch float32 Tensor of shape [3, H, W].
    """
    # Transpose HWC (Height, Width, Channels) to CHW (Channels, Height, Width)
    tensor = torch.from_numpy(img_np).permute(2, 0, 1).float()

    if apply_imagenet_norm:
        mean_t = torch.tensor(mean, dtype=torch.float32).view(3, 1, 1)
        std_t = torch.tensor(std, dtype=torch.float32).view(3, 1, 1)
        tensor = (tensor - mean_t) / std_t

    return tensor


# ==============================================================================
# END-TO-END DETERMINISTIC PREPROCESSING PIPELINE
# ==============================================================================

def preprocess_image(
    image: Union[Image.Image, np.ndarray, str, Path],
    size: Tuple[int, int] = IMAGE_SIZE,
    apply_imagenet_norm: bool = True,
    augmentation: Optional[Callable[[Image.Image], Image.Image]] = None,
) -> torch.Tensor:
    """Execute the locked 5-stage preprocessing pipeline with optional training augmentation.

    Stages:
        1. Resize -> (224, 224)
        [Optional training-only geometric augmentation applied to resized PIL image]
        2. White Balance -> Gray World adjustment
        3. Color Normalization -> [0.0, 1.0] continuous float representation
        4. Noise Removal -> Gaussian smoothing (3x3, sigma=0.5)
        5. Tensor Preparation -> Float32 tensor [3, 224, 224] with ImageNet standardization

    Args:
        image: Input as PIL Image, NumPy array, or path string/Path object.
        size: Target image dimensions (default: IMAGE_SIZE = (224, 224)).
        apply_imagenet_norm: If True, applies ImageNet mean/std standardization in Stage 5.
        augmentation: Optional callable applied to resized PIL image before pixel-level stages.

    Returns:
        PyTorch float32 Tensor with shape [3, 224, 224].
    """
    # Load and convert to RGB
    if isinstance(image, (str, Path)):
        pil_img = Image.open(image).convert("RGB")
    elif isinstance(image, np.ndarray):
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.ndim == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.ndim == 3 and image.shape[2] == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        pil_img = Image.fromarray(image.astype(np.uint8)).convert("RGB")
    elif isinstance(image, Image.Image):
        pil_img = image.convert("RGB")
    else:
        raise TypeError(f"Unsupported image input type: {type(image)}")

    # Stage 1: Resize
    resized_pil = resize_image(pil_img, size=size)

    # Optional training-only geometric augmentation (e.g. flip, rotation)
    if augmentation is not None:
        resized_pil = augmentation(resized_pil)

    img_np = np.array(resized_pil)

    # Stage 2: White Balance
    wb_np = white_balance_gray_world(img_np)

    # Stage 3: Color Normalization
    cn_np = color_normalize(wb_np)

    # Stage 4: Noise Removal
    denoised_np = noise_removal(cn_np, kernel_size=3, sigma=0.5)

    # Stage 5: Tensor Preparation
    tensor = prepare_tensor(denoised_np, apply_imagenet_norm=apply_imagenet_norm)

    return tensor


# ==============================================================================
# SEPARATE CALLABLE TRANSFORM OBJECTS
# ==============================================================================

class DeterministicPreprocessor:
    """Callable preprocessor for inference and validation.

    Ensures 100% deterministic preprocessing matching the locked 5-stage specification.
    """

    def __init__(
        self,
        size: Tuple[int, int] = IMAGE_SIZE,
        apply_imagenet_norm: bool = True,
    ) -> None:
        self.size = size
        self.apply_imagenet_norm = apply_imagenet_norm

    def __call__(self, image: Union[Image.Image, np.ndarray, str, Path]) -> torch.Tensor:
        return preprocess_image(
            image,
            size=self.size,
            apply_imagenet_norm=self.apply_imagenet_norm,
            augmentation=None,
        )


class AugmentedTrainingPreprocessor:
    """Callable preprocessor for model training with isolated geometric augmentations.

    Applies training-only geometric augmentations (random horizontal flip,
    mild rotation) followed by the exact locked core preprocessing stages:
    1. Resize -> (224, 224)
    [Training-only geometric augmentation]
    2. White Balance -> Gray World adjustment
    3. Color Normalization -> [0.0, 1.0] continuous float representation
    4. Noise Removal -> Gaussian smoothing (3x3, sigma=0.5)
    5. Tensor Preparation -> Float32 tensor [3, 224, 224] with ImageNet standardization
    """

    def __init__(
        self,
        size: Tuple[int, int] = IMAGE_SIZE,
        apply_imagenet_norm: bool = True,
        flip_prob: float = 0.5,
        rotation_degrees: float = 10.0,
    ) -> None:
        self.size = size
        self.apply_imagenet_norm = apply_imagenet_norm
        self.geometric_augmentations = transforms.Compose([
            transforms.RandomHorizontalFlip(p=flip_prob),
            transforms.RandomRotation(degrees=rotation_degrees),
        ])

    def __call__(self, image: Union[Image.Image, np.ndarray, str, Path]) -> torch.Tensor:
        return preprocess_image(
            image,
            size=self.size,
            apply_imagenet_norm=self.apply_imagenet_norm,
            augmentation=self.geometric_augmentations,
        )


def get_inference_transforms(
    size: Tuple[int, int] = IMAGE_SIZE,
    apply_imagenet_norm: bool = True,
) -> DeterministicPreprocessor:
    """Return the deterministic preprocessing transform pipeline for inference/evaluation."""
    return DeterministicPreprocessor(size=size, apply_imagenet_norm=apply_imagenet_norm)


def get_training_transforms(
    size: Tuple[int, int] = IMAGE_SIZE,
    apply_imagenet_norm: bool = True,
    flip_prob: float = 0.5,
    rotation_degrees: float = 10.0,
) -> AugmentedTrainingPreprocessor:
    """Return the training preprocessor pipeline incorporating core stages and isolated augmentation."""
    return AugmentedTrainingPreprocessor(
        size=size,
        apply_imagenet_norm=apply_imagenet_norm,
        flip_prob=flip_prob,
        rotation_degrees=rotation_degrees,
    )
