from pathlib import Path

import torch
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset

from src.config import CLASS_NAMES, NUM_CLASSES, TRAINING_DATA_DIR
from src.data.dataset import NeoHealthDataset
from src.data.preprocessing import get_inference_transforms
from src.models.efficientnet import create_efficientnet_b0


RANDOM_STATE = 42
BATCH_SIZE = 16
MODEL_PATH = Path("models/efficientnet_b0_best.pth")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)
    print("Loading dataset...")

    dataset = NeoHealthDataset(
        root_dir=TRAINING_DATA_DIR,
        transform=get_inference_transforms(),
        allowed_classes=CLASS_NAMES,
    )

    labels = [label for _, label in dataset.samples]
    indices = list(range(len(dataset)))

    _, val_indices = train_test_split(
        indices,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    val_dataset = Subset(dataset, val_indices)

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    print("Validation samples:", len(val_dataset))

    model = create_efficientnet_b0(
        num_classes=NUM_CLASSES,
        pretrained=False,
    ).to(device)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=False,
    )

    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.eval()

    all_predictions = []
    all_targets = []

    with torch.no_grad():
        for images, targets in val_loader:
            images = images.to(device)

            outputs = model(images)
            predictions = torch.argmax(outputs, dim=1)

            all_predictions.extend(predictions.cpu().tolist())
            all_targets.extend(targets.tolist())

    print("\nValidation Accuracy:")
    accuracy = sum(
        p == t for p, t in zip(all_predictions, all_targets)
    ) / len(all_targets)

    print(f"{accuracy:.4f} ({accuracy * 100:.2f}%)")

    print("\nClassification Report:")
    print(
        classification_report(
            all_targets,
            all_predictions,
            labels=list(range(NUM_CLASSES)),
            target_names=CLASS_NAMES,
            digits=4,
            zero_division=0,
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            all_targets,
            all_predictions,
            labels=list(range(NUM_CLASSES)),
        )
    )


if __name__ == "__main__":
    main()