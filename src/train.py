"""NeoHealth AI - Six-class EfficientNet-B0 training pipeline."""

from pathlib import Path
import sys

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import CLASS_NAMES, NUM_CLASSES
from src.data.dataset import NeoHealthDataset
from src.data.preprocessing import (
    get_training_transforms,
    get_inference_transforms,
)
from src.models.efficientnet import create_efficientnet_b0


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "neohealth-frontend"
    / "data"
    / "raw"
    / "training"
)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 1e-4
RANDOM_STATE = 42


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    print("\nCanonical classes:")
    for index, class_name in enumerate(CLASS_NAMES):
        print(f"  {index}: {class_name}")

    # Load the complete canonical six-class dataset.
    dataset = NeoHealthDataset(
        root_dir=DATA_DIR,
        transform=get_inference_transforms(),
        allowed_classes=CLASS_NAMES,
    )

    print("\nDataset summary:")
    print(dataset.get_summary())

    # Never train a final six-class model when a canonical class
    # has zero training samples.
    missing_classes = [
        class_name
        for class_name in CLASS_NAMES
        if dataset.class_counts[class_name] == 0
    ]

    if missing_classes:
        print("\nTRAINING STOPPED")
        print("The following canonical classes have no training images:")
        for class_name in missing_classes:
            print(f"  - {class_name}")

        print(
            "\nAdd valid training data for these classes before "
            "training the final six-class model."
        )
        return

    labels = [label for _, label in dataset.samples]
    indices = list(range(len(dataset)))

    train_indices, val_indices = train_test_split(
        indices,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    train_dataset_full = NeoHealthDataset(
        root_dir=DATA_DIR,
        transform=get_training_transforms(),
        allowed_classes=CLASS_NAMES,
    )

    val_dataset_full = NeoHealthDataset(
        root_dir=DATA_DIR,
        transform=get_inference_transforms(),
        allowed_classes=CLASS_NAMES,
    )

    train_dataset = Subset(train_dataset_full, train_indices)
    val_dataset = Subset(val_dataset_full, val_indices)

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    print("\nSplit:")
    print("  Training:", len(train_dataset))
    print("  Validation:", len(val_dataset))

    # Final model always has exactly six output classes.
    model = create_efficientnet_b0(
        num_classes=NUM_CLASSES,
        pretrained=True,
    ).to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    best_val_accuracy = 0.0

    for epoch in range(EPOCHS):
        model.train()

        running_loss = 0.0
        correct = 0
        total = 0

        for images, targets in train_loader:
            images = images.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, targets)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == targets).sum().item()
            total += targets.size(0)

        train_loss = running_loss / total
        train_accuracy = correct / total

        model.eval()

        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, targets in val_loader:
                images = images.to(device)
                targets = targets.to(device)

                outputs = model(images)
                predictions = outputs.argmax(dim=1)

                val_correct += (predictions == targets).sum().item()
                val_total += targets.size(0)

        val_accuracy = val_correct / val_total

        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_accuracy:.4f} | "
            f"Val Acc: {val_accuracy:.4f}"
        )

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy

            checkpoint = {
                "model_state_dict": model.state_dict(),
                "classes": CLASS_NAMES,
                "num_classes": NUM_CLASSES,
                "best_val_accuracy": best_val_accuracy,
            }

            output_path = MODEL_DIR / "efficientnet_b0_best.pth"

            torch.save(checkpoint, output_path)

            print("Saved:", output_path)

    print("\nBest validation accuracy:", best_val_accuracy)


if __name__ == "__main__":
    main()