"""NeoHealth AI - Grad-CAM explainability for EfficientNet-B0."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from src.config import CLASS_NAMES, NUM_CLASSES
from src.data.preprocessing import get_inference_transforms
from src.models.efficientnet import create_efficientnet_b0


MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "efficientnet_b0_best.pth"
)

RESULTS_DIR = PROJECT_ROOT / "results"


def load_model(device):
    """Load the trained six-class EfficientNet-B0."""

    model = create_efficientnet_b0(
        num_classes=NUM_CLASSES,
        pretrained=False,
    )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    return model


def generate_gradcam(
    image_path,
    model,
    device,
):
    """Generate a Grad-CAM heatmap for the predicted class."""

    transform = get_inference_transforms()

    with Image.open(image_path) as image:
        original = image.convert("RGB")

    tensor = transform(original).unsqueeze(0).to(device)
    tensor.requires_grad_(True)

    activations = []
    gradients = []

    target_layer = model.features[-1]

    def forward_hook(module, inputs, output):
        activations.append(output)

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    forward_handle = target_layer.register_forward_hook(
        forward_hook
    )

    backward_handle = target_layer.register_full_backward_hook(
        backward_hook
    )

    try:
        model.zero_grad()

        output = model(tensor)

        probabilities = torch.softmax(
            output,
            dim=1,
        )

        predicted_index = int(
            torch.argmax(
                probabilities,
                dim=1,
            ).item()
        )

        target_score = output[
            0,
            predicted_index,
        ]

        target_score.backward()

        feature_maps = activations[0]
        gradient = gradients[0]

        weights = gradient.mean(
            dim=(2, 3),
            keepdim=True,
        )

        cam = (
            weights * feature_maps
        ).sum(dim=1, keepdim=True)

        cam = F.relu(cam)

        cam = F.interpolate(
            cam,
            size=original.size[::-1],
            mode="bilinear",
            align_corners=False,
        )

        cam = cam.squeeze().detach().cpu().numpy()

        cam -= cam.min()

        if cam.max() > 0:
            cam /= cam.max()

        return (
            original,
            predicted_index,
            float(
                probabilities[
                    0,
                    predicted_index,
                ].item()
            ),
            cam,
        )

    finally:
        forward_handle.remove()
        backward_handle.remove()


def save_gradcam_overlay(
    original,
    cam,
    output_path,
):
    """Create and save a simple Grad-CAM overlay."""

    original_array = np.asarray(
        original.resize(
            (cam.shape[1], cam.shape[0])
        )
    ).astype(np.float32)

    heatmap = np.zeros_like(
        original_array
    )

    heatmap[:, :, 0] = cam * 255.0
    heatmap[:, :, 1] = (1.0 - cam) * 80.0

    overlay = (
        0.6 * original_array
        + 0.4 * heatmap
    )

    overlay = np.clip(
        overlay,
        0,
        255,
    ).astype(np.uint8)

    Image.fromarray(
        overlay
    ).save(output_path)


def main():
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    image_path = (
        PROJECT_ROOT
        / "neohealth-frontend"
        / "data"
        / "raw"
        / "training"
        / "Jaundice"
        / "jaundice (1).jpg"
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"Device: {device}")
    print(f"Image: {image_path}")

    model = load_model(device)

    (
        original,
        predicted_index,
        confidence,
        cam,
    ) = generate_gradcam(
        image_path,
        model,
        device,
    )

    predicted_class = CLASS_NAMES[
        predicted_index
    ]

    output_path = (
        RESULTS_DIR
        / "gradcam_jaundice.png"
    )

    save_gradcam_overlay(
        original,
        cam,
        output_path,
    )

    print(
        f"Prediction: {predicted_class}"
    )

    print(
        f"Confidence: "
        f"{confidence * 100:.2f}%"
    )

    print(
        f"Saved Grad-CAM: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()