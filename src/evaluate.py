"""NeoHealth AI - Six-class EfficientNet-B0 evaluation."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset

from src.config import CLASS_NAMES, NUM_CLASSES
from src.data.dataset import NeoHealthDataset
from src.data.preprocessing import get_inference_transforms
from src.models.efficientnet import create_efficientnet_b0


DATASET_ROOT = (
    PROJECT_ROOT
    / "neohealth-frontend"
    / "data"
    / "raw"
    / "training"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "efficientnet_b0_best.pth"
)

RESULTS_DIR = PROJECT_ROOT / "results"


def main():
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Device: {device}")
    print(f"Model: {MODEL_PATH}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    dataset = NeoHealthDataset(
        DATASET_ROOT,
        transform=get_inference_transforms(),
    )

    labels = [sample[1] for sample in dataset.samples]
    indices = list(range(len(dataset)))

    _, val_indices = train_test_split(
        indices,
        test_size=0.20,
        random_state=42,
        stratify=labels,
    )

    validation_dataset = Subset(
        dataset,
        val_indices,
    )

    loader = DataLoader(
        validation_dataset,
        batch_size=16,
        shuffle=False,
        num_workers=0,
    )

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

    all_predictions = []
    all_labels = []

    with torch.no_grad():
        for images, labels_batch in loader:
            images = images.to(device)

            outputs = model(images)

            predictions = torch.argmax(
                outputs,
                dim=1,
            ).cpu().tolist()

            all_predictions.extend(predictions)
            all_labels.extend(labels_batch.tolist())

    accuracy = accuracy_score(
        all_labels,
        all_predictions,
    )

    matrix = confusion_matrix(
        all_labels,
        all_predictions,
        labels=list(range(NUM_CLASSES)),
    )

    report = classification_report(
        all_labels,
        all_predictions,
        labels=list(range(NUM_CLASSES)),
        target_names=CLASS_NAMES,
        zero_division=0,
        digits=4,
    )

    print("\n" + "=" * 60)
    print("NEOHEALTH AI - MODEL EVALUATION")
    print("=" * 60)

    print(f"\nValidation samples: {len(all_labels)}")
    print(
        f"Accuracy: {accuracy:.4f} "
        f"({accuracy * 100:.2f}%)"
    )

    print("\nClassification Report:")
    print(report)

    print("Confusion Matrix:")
    print("Rows = Actual | Columns = Predicted")

    print("\nClasses:")
    for index, class_name in enumerate(CLASS_NAMES):
        print(f"  {index}: {class_name}")

    print()
    print(matrix)

    # Save confusion matrix figure.
    fig, ax = plt.subplots(
        figsize=(9, 7)
    )

    ax.imshow(matrix)

    ax.set(
        xticks=range(NUM_CLASSES),
        yticks=range(NUM_CLASSES),
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        xlabel="Predicted Class",
        ylabel="Actual Class",
        title="NeoHealth AI - Confusion Matrix",
    )

    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            ax.text(
                j,
                i,
                matrix[i, j],
                ha="center",
                va="center",
            )

    fig.tight_layout()

    output_path = (
        RESULTS_DIR
        / "confusion_matrix.png"
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(
        f"\nSaved confusion matrix: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()