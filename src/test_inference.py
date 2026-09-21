import sys
from pathlib import Path

sys.path.insert(0, "..")

from src.config import CLASS_NAMES
from src.inference import load_model, predict_image


model, device = load_model()

root = Path(r"data\raw\training")

print("\n" + "=" * 60)
print("NEOHEALTH AI - SIX-CLASS INFERENCE TEST")
print("=" * 60)

for class_name in CLASS_NAMES:
    class_dir = root / class_name
    image = next(class_dir.glob("*"))

    result = predict_image(
        image,
        model,
        device,
    )

    print(f"\nActual class: {class_name}")
    print(f"Image: {image.name}")
    print(f"Prediction: {result['prediction']}")
    print(
        f"Confidence: "
        f"{result['confidence_percent']:.2f}%"
    )
    print(f"Status: {result['status']}")

print("\n" + "=" * 60)