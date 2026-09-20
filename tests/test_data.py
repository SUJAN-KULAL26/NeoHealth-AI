"""Comprehensive unit tests for NeoHealth AI Data and Preprocessing modules.

Uses synthetic in-memory images exclusively (no fake medical images).
Validates:
- 5 locked preprocessing stages (Resize, White Balance, Color Normalization,
  Noise Removal, Tensor Preparation)
- Output tensor dimensions [3, 224, 224] and dtype float32
- Determinism for inference
- NeoHealthDataset loading, canonical class validation, and extension filtering
- PyTorch DataLoader compatibility
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader

from src.config import (
    CLASS_NAMES,
    CLASS_TO_IDX,
    IMAGE_SIZE,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from src.data.dataset import NeoHealthDataset
from src.data.preprocessing import (
    IMAGENET_MEAN,
    IMAGENET_STD,
    DeterministicPreprocessor,
    color_normalize,
    get_inference_transforms,
    get_training_transforms,
    noise_removal,
    prepare_tensor,
    preprocess_image,
    resize_image,
    white_balance_gray_world,
)


class TestPreprocessingStages(unittest.TestCase):
    """Unit tests for each of the five locked preprocessing stages individually."""

    def test_stage1_resize(self):
        """Stage 1: Resize arbitrary dimension images to exact (224, 224)."""
        # Test non-square dimensions
        img_small = Image.new("RGB", (100, 160), color=(120, 150, 180))
        resized = resize_image(img_small, size=IMAGE_SIZE)
        self.assertEqual(resized.size, (224, 224))

        # Test larger non-square dimensions
        img_large = Image.new("RGB", (640, 480), color=(50, 60, 70))
        resized_large = resize_image(img_large, size=IMAGE_SIZE)
        self.assertEqual(resized_large.size, (224, 224))

        # Test already (224, 224)
        img_exact = Image.new("RGB", (224, 224), color=(10, 20, 30))
        resized_exact = resize_image(img_exact, size=IMAGE_SIZE)
        self.assertEqual(resized_exact.size, (224, 224))

    def test_stage2_white_balance_gray_world(self):
        """Stage 2: White Balance adjusts color channel distribution towards neutral gray."""
        # Create an image with an intentionally strong yellow bias (high R and G, low B)
        biased_np = np.zeros((100, 100, 3), dtype=np.uint8)
        biased_np[:, :, 0] = 200  # R
        biased_np[:, :, 1] = 200  # G
        biased_np[:, :, 2] = 50   # B

        balanced = white_balance_gray_world(biased_np)
        self.assertEqual(balanced.shape, (100, 100, 3))
        self.assertEqual(balanced.dtype, np.float32)

        # In balanced output, all channel means should converge to the gray reference
        mean_r = np.mean(balanced[:, :, 0])
        mean_g = np.mean(balanced[:, :, 1])
        mean_b = np.mean(balanced[:, :, 2])
        self.assertAlmostEqual(mean_r, mean_g, delta=1.0)
        self.assertAlmostEqual(mean_g, mean_b, delta=1.0)

        # Test zero-division safety
        zero_img = np.zeros((10, 10, 3), dtype=np.uint8)
        balanced_zero = white_balance_gray_world(zero_img)
        self.assertEqual(balanced_zero.shape, (10, 10, 3))
        self.assertTrue(np.all(balanced_zero == 0.0))

    def test_stage3_color_normalization(self):
        """Stage 3: Color Normalization standardizes values to [0.0, 1.0] continuous float."""
        arr = np.array([[[0, 127, 255], [64, 191, 255]]], dtype=np.uint8)
        norm = color_normalize(arr)

        self.assertEqual(norm.dtype, np.float32)
        self.assertAlmostEqual(norm[0, 0, 0], 0.0, delta=1e-4)
        self.assertAlmostEqual(norm[0, 0, 1], 127.0 / 255.0, delta=1e-4)
        self.assertAlmostEqual(norm[0, 0, 2], 1.0, delta=1e-4)
        self.assertTrue(np.all(norm >= 0.0))
        self.assertTrue(np.all(norm <= 1.0))

    def test_stage4_noise_removal(self):
        """Stage 4: Noise Removal applies smoothing while preserving dimensions and range."""
        # Create noisy synthetic pattern
        np.random.seed(42)
        noisy = np.random.uniform(0.0, 1.0, size=(224, 224, 3)).astype(np.float32)
        denoised = noise_removal(noisy, kernel_size=3, sigma=0.5)

        self.assertEqual(denoised.shape, (224, 224, 3))
        self.assertEqual(denoised.dtype, np.float32)
        self.assertTrue(np.all(denoised >= 0.0))
        self.assertTrue(np.all(denoised <= 1.0))
        # Variance of denoised array should be lower than raw uniform noise
        self.assertLess(np.var(denoised), np.var(noisy))

    def test_stage5_tensor_preparation(self):
        """Stage 5: Tensor Preparation outputs [3, 224, 224] float32 with ImageNet norm."""
        arr = np.full((224, 224, 3), 0.5, dtype=np.float32)

        # Without ImageNet standardization
        raw_tensor = prepare_tensor(arr, apply_imagenet_norm=False)
        self.assertIsInstance(raw_tensor, torch.Tensor)
        self.assertEqual(raw_tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(raw_tensor.dtype, torch.float32)
        self.assertAlmostEqual(raw_tensor[0, 0, 0].item(), 0.5, delta=1e-4)

        # With ImageNet standardization
        norm_tensor = prepare_tensor(arr, apply_imagenet_norm=True)
        self.assertEqual(norm_tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(norm_tensor.dtype, torch.float32)

        # Channel 0 expected: (0.5 - 0.485) / 0.229
        expected_ch0 = (0.5 - IMAGENET_MEAN[0]) / IMAGENET_STD[0]
        self.assertAlmostEqual(norm_tensor[0, 0, 0].item(), expected_ch0, delta=1e-3)


class TestPreprocessImagePipeline(unittest.TestCase):
    """Unit tests for the end-to-end deterministic preprocessing pipeline."""

    def test_preprocess_from_pil_rgb(self):
        """Preprocess standard RGB PIL image."""
        img = Image.new("RGB", (320, 240), color=(180, 200, 220))
        tensor = preprocess_image(img)
        self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_preprocess_from_pil_rgba(self):
        """Preprocess RGBA PIL image, ensuring alpha channel is stripped."""
        img = Image.new("RGBA", (150, 150), color=(100, 150, 200, 128))
        tensor = preprocess_image(img)
        self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_preprocess_from_pil_grayscale(self):
        """Preprocess Grayscale ('L') image, converting to 3 channels."""
        img = Image.new("L", (200, 200), color=128)
        tensor = preprocess_image(img)
        self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_preprocess_from_numpy_array(self):
        """Preprocess NumPy uint8 array."""
        arr = np.random.randint(0, 256, size=(180, 250, 3), dtype=np.uint8)
        tensor = preprocess_image(arr)
        self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_deterministic_behavior(self):
        """Verify identical inputs yield bit-for-bit identical preprocessed tensors."""
        img = Image.new("RGB", (250, 250), color=(123, 45, 67))
        t1 = preprocess_image(img)
        t2 = preprocess_image(img)
        self.assertTrue(torch.equal(t1, t2))

    def test_inference_and_training_transform_separation(self):
        """Verify inference transform is deterministic while training transforms exist separately."""
        inf_transform = get_inference_transforms()
        train_transform = get_training_transforms()

        img = Image.new("RGB", (224, 224), color=(100, 120, 140))
        inf_tensor = inf_transform(img)
        train_tensor = train_transform(img)

        self.assertEqual(inf_tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(train_tensor.shape, torch.Size([3, 224, 224]))
        self.assertEqual(inf_tensor.dtype, torch.float32)
        self.assertEqual(train_tensor.dtype, torch.float32)


class TestNeoHealthDataset(unittest.TestCase):
    """Unit tests for the NeoHealthDataset class using temporary synthetic directories."""

    def setUp(self):
        """Create a temporary directory hierarchy with synthetic test images."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name)

        # Create subdirectories for canonical classes
        self.classes_to_create = ["Jaundice", "Normal", "Impetigo"]
        self.created_files = []

        for cls_name in self.classes_to_create:
            cls_dir = self.root_path / cls_name
            cls_dir.mkdir(parents=True, exist_ok=True)

            # Create synthetic images with different supported extensions
            img1 = Image.new("RGB", (100, 100), color=(200, 100, 50))
            img1_path = cls_dir / "img1.jpg"
            img1.save(img1_path)
            self.created_files.append(img1_path)

            img2 = Image.new("RGB", (150, 120), color=(100, 180, 220))
            img2_path = cls_dir / "img2.png"
            img2.save(img2_path)
            self.created_files.append(img2_path)

            img3 = Image.new("RGB", (110, 130), color=(50, 50, 50))
            img3_path = cls_dir / "img3.jpeg"
            img3.save(img3_path)
            self.created_files.append(img3_path)

            # Add an unsupported file that should be ignored
            unsupported_path = cls_dir / "notes.txt"
            unsupported_path.write_text("dataset notes")

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_dataset_loading_and_counts(self):
        """Verify dataset correctly loads all supported images and ignores unsupported files."""
        dataset = NeoHealthDataset(root_dir=self.root_path)

        # 3 classes * 3 valid images each = 9 samples
        self.assertEqual(len(dataset), 9)

        summary = dataset.get_summary()
        self.assertEqual(summary["total_samples"], 9)
        self.assertEqual(dataset.class_counts["Jaundice"], 3)
        self.assertEqual(dataset.class_counts["Normal"], 3)
        self.assertEqual(dataset.class_counts["Impetigo"], 3)
        self.assertEqual(dataset.class_counts["Atopic Dermatitis"], 0)

    def test_dataset_canonical_indices(self):
        """Verify that label indices match canonical CLASS_TO_IDX."""
        dataset = NeoHealthDataset(root_dir=self.root_path, return_path=True)

        for i in range(len(dataset)):
            tensor, label_idx, file_path = dataset[i]
            self.assertEqual(tensor.shape, torch.Size([3, 224, 224]))
            self.assertEqual(tensor.dtype, torch.float32)

            path_obj = Path(file_path)
            parent_name = path_obj.parent.name
            expected_idx = CLASS_TO_IDX[parent_name]
            self.assertEqual(label_idx, expected_idx)

    def test_case_insensitive_directory_resolution(self):
        """Verify lowercase class directories (e.g. 'jaundice', 'normal') resolve to canonical names."""
        with tempfile.TemporaryDirectory() as temp_lower:
            root = Path(temp_lower)
            (root / "jaundice").mkdir()
            (root / "normal").mkdir()

            img = Image.new("RGB", (50, 50), color=(100, 100, 100))
            img.save(root / "jaundice" / "sample1.jpg")
            img.save(root / "normal" / "sample2.png")

            dataset = NeoHealthDataset(root_dir=root)
            self.assertEqual(len(dataset), 2)
            self.assertEqual(dataset.class_counts["Jaundice"], 1)
            self.assertEqual(dataset.class_counts["Normal"], 1)

    def test_nonexistent_directory_raises_error(self):
        """Verify FileNotFoundError is raised when root_dir does not exist."""
        nonexistent = self.root_path / "does_not_exist"
        with self.assertRaises(FileNotFoundError):
            NeoHealthDataset(root_dir=nonexistent)

    def test_unknown_class_directory_raises_error(self):
        """Verify ValueError is raised when an unrecognized class folder is encountered."""
        with tempfile.TemporaryDirectory() as temp_err:
            root = Path(temp_err)
            (root / "UnknownCondition").mkdir()
            img = Image.new("RGB", (50, 50), color=(100, 100, 100))
            img.save(root / "UnknownCondition" / "test.jpg")

            with self.assertRaises(ValueError) as ctx:
                NeoHealthDataset(root_dir=root)
            self.assertIn("UnknownCondition", str(ctx.exception))

    def test_empty_dataset_raises_runtime_error(self):
        """Verify RuntimeError is raised when no supported images are discovered."""
        with tempfile.TemporaryDirectory() as temp_empty:
            root = Path(temp_empty)
            (root / "Normal").mkdir()
            (root / "Normal" / "file.txt").write_text("not an image")

            with self.assertRaises(RuntimeError):
                NeoHealthDataset(root_dir=root)

    def test_dataloader_batch_generation(self):
        """Verify compatibility with torch.utils.data.DataLoader."""
        dataset = NeoHealthDataset(root_dir=self.root_path)
        loader = DataLoader(dataset, batch_size=4, shuffle=False)

        batch_images, batch_labels = next(iter(loader))
        self.assertEqual(batch_images.shape, torch.Size([4, 3, 224, 224]))
        self.assertEqual(batch_labels.shape, torch.Size([4]))
        self.assertEqual(batch_images.dtype, torch.float32)


if __name__ == "__main__":
    unittest.main()
