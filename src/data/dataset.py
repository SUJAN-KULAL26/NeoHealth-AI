"""NeoHealth AI — Dataset Module.

Implements PyTorch Dataset for the canonical six infant health classes:
1. Jaundice
2. Atopic Dermatitis
3. Impetigo
4. Cradle Cap
5. Neonatal Acne
6. Normal

Supports directory-based dataset structures where image files are organized in
subdirectories named by class (e.g., root_dir/Jaundice/img1.jpg).
Case-insensitive matching is supported to accommodate lowercase directory conventions
(e.g., "jaundice" -> "Jaundice") without altering canonical class identities.
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple, Union
import warnings

from PIL import Image
import torch
from torch.utils.data import Dataset

from src.config import (
    CLASS_NAMES,
    CLASS_TO_IDX,
    IMAGE_SIZE,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from src.data.preprocessing import DeterministicPreprocessor, preprocess_image


class NeoHealthDataset(Dataset):
    """PyTorch Dataset for NeoHealth AI 6-class infant health condition screening.

    Attributes:
        root_dir: Base directory containing class subdirectories.
        transform: Optional callable transform applied to each PIL Image or path.
                   Defaults to deterministic 5-stage preprocessing pipeline.
        return_path: If True, __getitem__ returns (tensor, label_idx, path_str).
                     If False (default), returns (tensor, label_idx).
        samples: List of (image_path, canonical_label_index) tuples.
        class_counts: Dictionary mapping canonical class names to sample counts.
    """

    def __init__(
        self,
        root_dir: Union[str, Path],
        transform: Optional[Callable[[Union[Image.Image, Path]], torch.Tensor]] = None,
        return_path: bool = False,
        supported_extensions: Optional[Set[str]] = None,
        allowed_classes: Optional[Tuple[str, ...]] = None,
    ) -> None:
        """Initialize the NeoHealthDataset.

        Args:
            root_dir: Path to directory containing class subfolders.
            transform: Callable preprocessing transform. Default is DeterministicPreprocessor.
            return_path: Whether to return file path in __getitem__.
            supported_extensions: Set of allowed lowercase extensions. Defaults to config.SUPPORTED_IMAGE_EXTENSIONS.
            allowed_classes: Subset of canonical classes to load. Defaults to all 6 canonical classes.

        Raises:
            FileNotFoundError: If root_dir does not exist.
            ValueError: If an unrecognized non-canonical class folder is encountered.
            RuntimeError: If no valid image files are discovered.
        """
        self.root_dir = Path(root_dir).resolve()
        if not self.root_dir.exists() or not self.root_dir.is_dir():
            raise FileNotFoundError(f"Dataset root directory does not exist: {self.root_dir}")

        self.transform = transform if transform is not None else DeterministicPreprocessor(size=IMAGE_SIZE)
        self.return_path = return_path
        self.supported_extensions = (
            supported_extensions if supported_extensions is not None else SUPPORTED_IMAGE_EXTENSIONS
        )

        # Mapping for case-insensitive class directory resolution to canonical names
        self._canonical_lookup: Dict[str, str] = {
            name.lower(): name for name in CLASS_NAMES
        }

        target_classes = allowed_classes if allowed_classes is not None else CLASS_NAMES
        for cls in target_classes:
            if cls not in CLASS_NAMES:
                raise ValueError(
                    f"Class '{cls}' is not one of the locked canonical classes: {CLASS_NAMES}"
                )
        self._target_classes_set = set(target_classes)

        self.samples: List[Tuple[Path, int]] = []
        self.class_counts: Dict[str, int] = {name: 0 for name in CLASS_NAMES}

        self._discover_samples()

    def _discover_samples(self) -> None:
        """Scan root directory and collect valid image samples mapped to canonical class indices."""
        subdirs = [p for p in self.root_dir.iterdir() if p.is_dir()]

        for subdir in sorted(subdirs):
            dir_name = subdir.name.strip()
            # Ignore hidden or system directories
            if dir_name.startswith((".", "__")):
                continue

            # Resolve directory name to canonical class
            canonical_name = self._resolve_canonical_name(dir_name)
            if canonical_name is None:
                raise ValueError(
                    f"Directory '{dir_name}' in {self.root_dir} does not match any canonical class "
                    f"in locked scope: {CLASS_NAMES}"
                )

            if canonical_name not in self._target_classes_set:
                continue

            class_idx = CLASS_TO_IDX[canonical_name]

            # Discover image files with supported extensions
            for file_path in sorted(subdir.iterdir()):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    self.samples.append((file_path, class_idx))
                    self.class_counts[canonical_name] += 1

        if len(self.samples) == 0:
            raise RuntimeError(
                f"No valid image files with extensions {self.supported_extensions} "
                f"found in class subdirectories under {self.root_dir}."
            )

    def _resolve_canonical_name(self, dir_name: str) -> Optional[str]:
        """Resolve a directory name to its canonical class name."""
        # Exact match
        if dir_name in CLASS_NAMES:
            return dir_name

        # Case-insensitive match
        normalized = dir_name.lower().strip()
        if normalized in self._canonical_lookup:
            return self._canonical_lookup[normalized]

        # Common hyphen/underscore replacements (e.g. "atopic_dermatitis" -> "Atopic Dermatitis")
        spaced = normalized.replace("_", " ").replace("-", " ")
        if spaced in self._canonical_lookup:
            return self._canonical_lookup[spaced]

        return None

    def __len__(self) -> int:
        """Total number of discovered samples."""
        return len(self.samples)

    def __getitem__(self, idx: int) -> Union[Tuple[torch.Tensor, int], Tuple[torch.Tensor, int, str]]:
        """Retrieve and preprocess image sample at the given index.

        Args:
            idx: Sample index.

        Returns:
            If return_path is False: (image_tensor, class_idx)
            If return_path is True: (image_tensor, class_idx, image_path_str)
        """
        img_path, class_idx = self.samples[idx]

        try:
            # Open with PIL and guarantee RGB format
            with Image.open(img_path) as img:
                rgb_img = img.convert("RGB")
                tensor = self.transform(rgb_img)
        except Exception as err:
            raise RuntimeError(f"Error loading image at {img_path}: {err}") from err

        if self.return_path:
            return tensor, class_idx, str(img_path)
        return tensor, class_idx

    @property
    def classes(self) -> Tuple[str, ...]:
        """Return the canonical class names."""
        return CLASS_NAMES

    @property
    def class_to_idx(self) -> Dict[str, int]:
        """Return the canonical class to index mapping."""
        return CLASS_TO_IDX

    def get_summary(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """Return a structured summary of loaded dataset samples."""
        return {
            "total_samples": len(self.samples),
            "class_counts": {k: v for k, v in self.class_counts.items() if v > 0},
            "root_dir": str(self.root_dir),
        }
