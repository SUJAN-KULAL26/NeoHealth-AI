"""Unit tests for NeoHealth AI EfficientNet-B0 model architecture.

Validates:
1. EfficientNet-B0 creation without weight downloads (pretrained=False).
2. Classification head output dimension matches canonical NUM_CLASSES (6).
3. Classification head is an nn.Linear layer.
4. Input feature dimension to linear head is exactly 1280.
5. Existing dropout layer in classifier is preserved.
6. Forward pass produces tensor of shape (batch_size, NUM_CLASSES).
"""

import unittest

import torch
import torch.nn as nn

from src.config import NUM_CLASSES
from src.models.efficientnet import create_efficientnet_b0


class TestEfficientNetB0Model(unittest.TestCase):
    """Unit tests for EfficientNet-B0 model adaptation."""

    def test_01_create_model_without_pretrained_weights(self) -> None:
        """1. Model can be instantiated with pretrained=False without network calls."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        self.assertIsInstance(model, nn.Module)

    def test_02_classification_head_output_dimension(self) -> None:
        """2. Classification head output features equals canonical NUM_CLASSES (6)."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        head = model.classifier[1]
        self.assertEqual(head.out_features, NUM_CLASSES)
        self.assertEqual(head.out_features, 6)

    def test_03_classification_head_is_linear(self) -> None:
        """3. Classification head is an instance of torch.nn.Linear."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        self.assertIsInstance(model.classifier[1], nn.Linear)

    def test_04_classification_head_in_features(self) -> None:
        """4. Input features to linear classification head remain 1280."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        self.assertEqual(model.classifier[1].in_features, 1280)

    def test_05_dropout_layer_preserved(self) -> None:
        """5. Existing dropout layer in classifier sequential block is preserved."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        dropout_layer = model.classifier[0]
        self.assertIsInstance(dropout_layer, nn.Dropout)
        self.assertAlmostEqual(dropout_layer.p, 0.2)

    def test_06_forward_pass_output_shape(self) -> None:
        """6. Forward pass with synthetic input produces (batch_size, NUM_CLASSES)."""
        model = create_efficientnet_b0(num_classes=NUM_CLASSES, pretrained=False)
        model.eval()

        batch_size = 2
        synthetic_input = torch.randn(batch_size, 3, 224, 224)
        with torch.no_grad():
            output = model(synthetic_input)

        self.assertEqual(output.shape, (batch_size, NUM_CLASSES))
        self.assertEqual(output.shape, (2, 6))


if __name__ == "__main__":
    unittest.main()
