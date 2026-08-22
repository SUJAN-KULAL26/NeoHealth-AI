"""EfficientNet-B0 Model Architecture for NeoHealth AI.

This module implements transfer learning using EfficientNet-B0 pretrained on
ImageNet (EfficientNet_B0_Weights.IMAGENET1K_V1). The original classification head
is replaced with a linear layer producing outputs for the canonical NeoHealth AI
classes.
"""

from typing import Optional
import torch.nn as nn
from torchvision.models import EfficientNet, EfficientNet_B0_Weights, efficientnet_b0

from src.config import NUM_CLASSES


def create_efficientnet_b0(
    num_classes: int = NUM_CLASSES,
    pretrained: bool = True,
    weights: Optional[EfficientNet_B0_Weights] = None,
) -> EfficientNet:
    """Build an EfficientNet-B0 model for NeoHealth AI transfer learning.

    EfficientNet-B0 pretrained on ImageNet is adapted by replacing its original
    ImageNet classification head with a linear layer outputting logits for the
    NeoHealth AI disease classes.

    Args:
        num_classes: Number of target output classes (default: NUM_CLASSES from src.config).
        pretrained: If True and weights is None, loads EfficientNet_B0_Weights.IMAGENET1K_V1.
        weights: Optional explicit EfficientNet_B0_Weights instance. Overrides pretrained if provided.

    Returns:
        Adapted EfficientNet model instance.
    """
    if weights is None and pretrained:
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1

    model = efficientnet_b0(weights=weights)

    in_features: int = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features=in_features, out_features=num_classes)

    return model
