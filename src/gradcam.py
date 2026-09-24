"""
Grad-CAM Explainability for NeoHealth AI.

Generates a focused Grad-CAM visualization for the EfficientNet-B0 model
without changing model predictions.
Compatible with both the FastAPI backend and Streamlit demo.
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import cv2
import numpy as np
import torch
from PIL import Image

from src.data.preprocessing import get_inference_transforms


def _find_target_layer(model: torch.nn.Module):
    """Get the final convolutional feature layer from EfficientNet-B0."""
    return model.features[-1]


def _normalize_heatmap(heatmap: np.ndarray) -> np.ndarray:
    """Normalize heatmap to the range [0, 1]."""
    heatmap = np.maximum(heatmap, 0)

    max_value = heatmap.max()
    if max_value > 0:
        heatmap = heatmap / max_value

    return heatmap


def _enhance_heatmap(
    heatmap: np.ndarray,
    threshold: float = 0.35,
    gamma: float = 0.7,
) -> np.ndarray:
    """
    Remove weak activations and enhance stronger activations.

    threshold:
        Activations below this value are suppressed.
    gamma:
        Values below 1 increase the visual strength of high activations.
    """
    enhanced = heatmap.copy()

    # Remove weak activations.
    enhanced[enhanced < threshold] = 0.0

    # Re-normalize after thresholding.
    max_value = enhanced.max()
    if max_value > 0:
        enhanced = enhanced / max_value

    # Increase visibility of stronger regions.
    enhanced = np.power(enhanced, gamma)

    return enhanced


def create_gradcam_overlay(
    original_image: Union[Image.Image, np.ndarray],
    heatmap: np.ndarray,
    alpha: float = 0.65,
) -> Image.Image:
    """Create a blended Grad-CAM overlay image as a PIL Image."""
    if isinstance(original_image, Image.Image):
        image_rgb = np.array(original_image.convert("RGB"))
    else:
        image_rgb = np.array(original_image).astype(np.uint8)

    height, width = image_rgb.shape[:2]

    resized_heatmap = cv2.resize(
        heatmap,
        (width, height),
        interpolation=cv2.INTER_CUBIC,
    )
    resized_heatmap = np.clip(resized_heatmap, 0.0, 1.0)

    # Convert to 8-bit for colormap application.
    heatmap_uint8 = np.uint8(255 * resized_heatmap)

    colored_heatmap = cv2.applyColorMap(
        heatmap_uint8,
        cv2.COLORMAP_JET,
    )
    colored_heatmap = cv2.cvtColor(
        colored_heatmap,
        cv2.COLOR_BGR2RGB,
    )

    # Create an activation mask so weak regions don't dominate the image.
    mask = resized_heatmap[..., None]
    effective_alpha = alpha * mask

    overlay = (
        image_rgb.astype(np.float32) * (1.0 - effective_alpha)
        + colored_heatmap.astype(np.float32) * effective_alpha
    )
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    return Image.fromarray(overlay)


def save_gradcam_overlay(
    original_image: Union[Image.Image, np.ndarray],
    heatmap: np.ndarray,
    output_path: Union[str, Path],
    alpha: float = 0.65,
) -> str:
    """Create and save a bright Grad-CAM overlay to the specified file path."""
    output = create_gradcam_overlay(original_image, heatmap, alpha=alpha)

    path_obj = Path(output_path)
    path_obj.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.save(str(path_obj))
    return str(path_obj)


def generate_gradcam(
    image_path: Optional[Union[str, Path, Image.Image]] = None,
    model: Optional[torch.nn.Module] = None,
    device: Optional[torch.device] = None,
    output_path: Optional[Union[str, Path]] = None,
    image: Optional[Union[str, Path, Image.Image]] = None,
) -> Union[Tuple[Image.Image, int, float, np.ndarray], str, Image.Image]:
    """
    Generate a focused Grad-CAM visualization for the predicted class.

    Compatible with:
      1. FastAPI backend:
         (original, predicted_index, gradcam_confidence, cam) = generate_gradcam(temporary_input, MODEL, DEVICE)
      2. Streamlit demo app:
         gradcam_image = generate_gradcam(image=image, model=model, device=device)
      3. Standalone saving:
         path = generate_gradcam(image_path, model, device, output_path="out.png")
    """
    if model is None:
        raise ValueError("Model must be provided to generate_gradcam.")

    # Resolve input image
    raw_input = image if image is not None else image_path
    if raw_input is None:
        raise ValueError("An image or image_path must be provided.")

    if isinstance(raw_input, Image.Image):
        original = raw_input.convert("RGB")
    else:
        with Image.open(raw_input) as img:
            original = img.convert("RGB")

    if device is None:
        device = next(model.parameters()).device

    model.eval()

    transform = get_inference_transforms()
    input_tensor = transform(original).unsqueeze(0).to(device)

    activations = None
    gradients = None

    target_layer = _find_target_layer(model)

    def forward_hook(module, inputs, output):
        nonlocal activations
        activations = output

    def backward_hook(module, grad_input, grad_output):
        nonlocal gradients
        gradients = grad_output[0]

    forward_handle = target_layer.register_forward_hook(forward_hook)
    backward_handle = target_layer.register_full_backward_hook(backward_hook)

    try:
        model.zero_grad(set_to_none=True)

        with torch.enable_grad():
            output = model(input_tensor)
            probabilities = torch.softmax(output, dim=1)

            target_class = int(torch.argmax(output, dim=1).item())
            confidence = float(probabilities[0, target_class].item())

            score = output[0, target_class]
            score.backward()

        if activations is None or gradients is None:
            raise RuntimeError("Grad-CAM could not capture activations or gradients.")

        activation = activations[0]
        gradient = gradients[0]

        weights_cam = gradient.mean(
            dim=(1, 2),
            keepdim=True,
        )

        cam = (weights_cam * activation).sum(dim=0)
        cam = torch.relu(cam)

        heatmap = cam.detach().cpu().numpy()
        heatmap = _normalize_heatmap(heatmap)
        heatmap = _enhance_heatmap(heatmap, threshold=0.35, gamma=0.7)

        # 1. If explicit output_path was requested
        if output_path is not None:
            return save_gradcam_overlay(original, heatmap, output_path)

        # 2. If called with keyword image=... and expecting a PIL image directly (e.g. app.py)
        if image is not None and not isinstance(image, (str, Path)):
            return create_gradcam_overlay(original, heatmap)

        # 3. Default canonical contract expected by api/main.py:
        # (original, predicted_index, gradcam_confidence, cam)
        return (
            original,
            target_class,
            confidence,
            heatmap,
        )

    finally:
        forward_handle.remove()
        backward_handle.remove()