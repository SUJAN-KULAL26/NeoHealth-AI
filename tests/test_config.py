"""Sanity tests for canonical configuration and locked scope using Python standard library."""

import unittest
from pathlib import Path

from src.config import (
    BASE_DIR,
    CLASS_NAMES,
    CLASS_TO_IDX,
    DATA_DIR,
    DISCLAIMER_TEXT,
    EXPERIMENTS_DIR,
    IDX_TO_CLASS,
    IMAGE_SIZE,
    MODELS_DIR,
    NUM_CLASSES,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    SUPPORTED_IMAGE_EXTENSIONS,
    TRAINING_DATA_DIR,
)



class TestConfig(unittest.TestCase):
    def test_class_count_and_exact_names(self):
        """Verify exactly six classes and exact canonical class names."""
        expected_classes = (
            "Jaundice",
            "Atopic Dermatitis",
            "Impetigo",
            "Cradle Cap",
            "Neonatal Acne",
            "Normal",
        )
        self.assertEqual(CLASS_NAMES, expected_classes)
        self.assertEqual(len(CLASS_NAMES), 6)
        self.assertEqual(NUM_CLASSES, 6)

    def test_class_index_mappings(self):
        """Verify bidirectional mapping consistency between names and indices."""
        self.assertEqual(len(CLASS_TO_IDX), 6)
        self.assertEqual(len(IDX_TO_CLASS), 6)

        for idx, name in enumerate(CLASS_NAMES):
            self.assertEqual(CLASS_TO_IDX[name], idx)
            self.assertEqual(IDX_TO_CLASS[idx], name)

    def test_supported_image_extensions(self):
        """Verify supported image extensions include JPG, JPEG, and PNG."""
        expected_extensions = {".jpg", ".jpeg", ".png"}
        self.assertEqual(SUPPORTED_IMAGE_EXTENSIONS, expected_extensions)

    def test_initial_image_size(self):
        """Verify initial image dimensions are (224, 224)."""
        self.assertEqual(IMAGE_SIZE, (224, 224))

    def test_screening_disclaimer(self):
        """Verify the mandatory screening disclaimer text."""
        self.assertEqual(
            DISCLAIMER_TEXT, "EARLY SCREENING TOOL — NOT A MEDICAL DIAGNOSIS"
        )

    def test_path_definitions(self):
        """Verify project path definitions are correct Path instances without creating directories."""
        self.assertIsInstance(BASE_DIR, Path)
        self.assertIsInstance(DATA_DIR, Path)
        self.assertIsInstance(RAW_DATA_DIR, Path)
        self.assertIsInstance(PROCESSED_DATA_DIR, Path)
        self.assertIsInstance(MODELS_DIR, Path)
        self.assertIsInstance(EXPERIMENTS_DIR, Path)
        self.assertIsInstance(TRAINING_DATA_DIR, Path)

        self.assertEqual(DATA_DIR, BASE_DIR / "data")
        self.assertEqual(RAW_DATA_DIR, BASE_DIR / "data" / "raw")
        self.assertEqual(PROCESSED_DATA_DIR, BASE_DIR / "data" / "processed")
        self.assertEqual(MODELS_DIR, BASE_DIR / "models")
        self.assertEqual(EXPERIMENTS_DIR, BASE_DIR / "experiments" / "runs")
        self.assertEqual(
            TRAINING_DATA_DIR,
            BASE_DIR / "neohealth-frontend" / "data" / "raw" / "training",
        )



if __name__ == "__main__":
    unittest.main()
