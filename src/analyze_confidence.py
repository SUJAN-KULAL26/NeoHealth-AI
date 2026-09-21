"""NeoHealth AI - Validation confidence analysis."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
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

CONFIDENCE_THRESHOLD = 0.70


def main():
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Device: {device}")

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

    total = 0
    correct = 0
    confident_total = 0
    confident_correct = 0
    uncertain_total = 0
    uncertain_correct = 0

    class_stats = {
        class_name: {
            "total": 0,
            "correct": 0,
            "confident": 0,
            "uncertain": 0,
        }
        for class_name in CLASS_NAMES
    }

    with torch.no_grad():
        for images, labels_batch in loader:
            images = images.to(device)

            logits = model(images)
            probabilities = torch.softmax(
                logits,
                dim=1,
            )

            confidence, predictions = torch.max(
                probabilities,
                dim=1,
            )

            for true_label, prediction, conf in zip(
                labels_batch.tolist(),
                predictions.cpu().tolist(),
                confidence.cpu().tolist(),
            ):
                total += 1

                is_correct = (
                    true_label == prediction
                )

                if is_correct:
                    correct += 1

                is_confident = (
                    conf >= CONFIDENCE_THRESHOLD
                )

                class_name = CLASS_NAMES[true_label]

                class_stats[class_name]["total"] += 1

                if is_correct:
                    class_stats[class_name]["correct"] += 1

                if is_confident:
                    confident_total += 1
                    class_stats[class_name]["confident"] += 1

                    if is_correct:
                        confident_correct += 1
                else:
                    uncertain_total += 1
                    class_stats[class_name]["uncertain"] += 1

                    if is_correct:
                        uncertain_correct += 1

    print("\n" + "=" * 65)
    print("NEOHEALTH AI - CONFIDENCE ANALYSIS")
    print("=" * 65)

    print(f"\nValidation samples: {total}")
    print(
        f"Overall accuracy: "
        f"{correct / total * 100:.2f}%"
    )

    print(
        f"\nConfidence threshold: "
        f"{CONFIDENCE_THRESHOLD:.2f}"
    )

    print(
        f"\nConfident predictions (>= 70%): "
        f"{confident_total} / {total} "
        f"({confident_total / total * 100:.2f}%)"
    )

    print(
        f"Correct among confident: "
        f"{confident_correct} / {confident_total} "
        f"({confident_correct / confident_total * 100:.2f}%)"
        if confident_total
        else "Correct among confident: N/A"
    )

    print(
        f"\nUncertain predictions (< 70%): "
        f"{uncertain_total} / {total} "
        f"({uncertain_total / total * 100:.2f}%)"
    )

    print(
        f"Correct among uncertain: "
        f"{uncertain_correct} / {uncertain_total} "
        f"({uncertain_correct / uncertain_total * 100:.2f}%)"
        if uncertain_total
        else "Correct among uncertain: N/A"
    )

    print("\nPer-class confidence distribution:")

    for class_name in CLASS_NAMES:
        stats = class_stats[class_name]

        confident_percentage = (
            stats["confident"]
            / stats["total"]
            * 100
        )

        print(
            f"\n{class_name}:"
        )
        print(
            f"  Samples: {stats['total']}"
        )
        print(
            f"  Correct: {stats['correct']}"
        )
        print(
            f"  >= 70% confidence: "
            f"{stats['confident']} "
            f"({confident_percentage:.2f}%)"
        )
        print(
            f"  < 70% confidence: "
            f"{stats['uncertain']}"
        )


if __name__ == "__main__":
    main()