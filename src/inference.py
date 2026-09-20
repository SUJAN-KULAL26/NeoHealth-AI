"""NeoHealth AI - Six-class EfficientNet-B0 inference."""

from pathlib import Path
from typing import Dict

import torch
from PIL import Image

from src.config import CLASS_NAMES, NUM_CLASSES
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
    model_path: Path = MODEL_PATH,
    device: torch.device | None = None,
):
    """Load the canonical six-class EfficientNet-B0 checkpoint."""

    if device is None:
        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    model = create_efficientnet_b0(
        num_classes=NUM_CLASSES,
        pretrained=False,
    )

    checkpoint = torch.load(
        model_path,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    return model, device


def predict_image(
    image_path: str | Path,
    model,
    device: torch.device,
) -> Dict[str, object]:
    """Run six-class prediction with confidence-aware screening."""

    transform = get_inference_transforms()

    image_path = Path(image_path)

    with Image.open(image_path) as image:
        image = image.convert("RGB")
        tensor = transform(image).unsqueeze(0).to(device)

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
    }