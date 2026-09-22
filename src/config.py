"""NeoHealth AI — Canonical Configuration Module.

Canonical project constants and definitions:
- Locked 6-class disease scope
- Directory path definitions
- Supported image extensions
- Initial image input size
- Medical screening disclaimer
"""

from pathlib import Path
from typing import Dict, Set, Tuple

# ==============================================================================
# CANONICAL SIX-CLASS SCOPE
# ==============================================================================
CLASS_NAMES: Tuple[str, ...] = (
    "Jaundice",
    "Atopic Dermatitis",
    "Impetigo",
    "Cradle Cap",
    "Neonatal Acne",
    "Normal",
)

NUM_CLASSES: int = 6

CLASS_TO_IDX: Dict[str, int] = {name: idx for idx, name in enumerate(CLASS_NAMES)}
IDX_TO_CLASS: Dict[int, str] = {idx: name for idx, name in enumerate(CLASS_NAMES)}

# ==============================================================================
# MEDICAL DISCLAIMER
# ==============================================================================
DISCLAIMER_TEXT: str = "EARLY SCREENING TOOL — NOT A MEDICAL DIAGNOSIS"

# ==============================================================================
# INPUT SPECIFICATIONS
# ==============================================================================
SUPPORTED_IMAGE_EXTENSIONS: Set[str] = {".jpg", ".jpeg", ".png"}
IMAGE_SIZE: Tuple[int, int] = (224, 224)

# ==============================================================================
# PROJECT DIRECTORIES (pathlib-based, not auto-created on import)
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
MODELS_DIR: Path = BASE_DIR / "models"
EXPERIMENTS_DIR: Path = BASE_DIR / "experiments" / "runs"
TRAINING_DATA_DIR: Path = (
    BASE_DIR / "neohealth-frontend" / "data" / "raw" / "training"
)
