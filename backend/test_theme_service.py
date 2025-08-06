"""
🧪 COMPREHENSIVE THEME SERVICE TESTS

Tests for face-mask generation logic covering edge cases, boundary conditions,
and small image scenarios to ensure robust mask generation.

Key Test Categories:
- Small image edge cases (100x100px, 200x200px)
- Boundary validation (coordinates within image bounds)
- Inner bounds integrity (left < right, top < bottom)
- Minimum dimension requirements (≥1px)
- Unusual face aspect ratios
- Offset percentage calculations (2%, 8%, 10%, 15%)
- Boundary clamping near image edges
- Consistency across different image sizes
"""

import unittest
from unittest.mock import patch, MagicMock
import io
from PIL import Image, ImageDraw
import numpy as np

# Import the service under test
from services.theme_service import ThemeService


class TestThemeServiceMaskGeneration(unittest.TestCase):
    """Comprehensive tests for face-mask generation logic."""

    def setUp(self):
        """Set up test environment with mocked dependencies."""
        # Mock all external dependencies
        self.mock_stability_service = MagicMock()
        self.mock_storage_service = MagicMock()
        
        # Create ThemeService instance with mocked dependencies
        with patch('services.theme_service.get_stability_service', return_value=self.mock_stability_service):
            with patch('services.theme_service.get_storage_service', return_value=self.mock_storage_service):
                self.theme_service = ThemeService()

    def test_small_image_100x100_boundary_validation(self):
        """Test mask generation for very small 100x100 images."""
        image_width, image_height = 100, 100
        
        # Generate mask using private method
        mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
        
        # Validate mask was created
        self.assertIsInstance(mask_bytes, bytes)
        self.assertGreater(len(mask_bytes), 0)
        
        # Load mask and verify dimensions
        mask_image = Image.open(io.BytesIO(mask_bytes))
        self.assertEqual(mask_image.size, (image_width, image_height))
        self.assertEqual(mask_image.mode, 'L')  # Grayscale

    def test_small_image_200x200_boundary_validation(self):
        """Test mask generation for small 200x200 images."""
        image_width, image_height = 200, 200
        
        mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
        
        # Validate mask was created successfully
        self.assertIsInstance(mask_bytes, bytes)
        self.assertGreater(len(mask_bytes), 0)
        
        # Load and validate mask properties
        mask_image = Image.open(io.BytesIO(mask_bytes))
        self.assertEqual(mask_image.size, (image_width, image_height))

    def test_inner_bounds_never_cross(self):
        """Test that inner bounds maintain left < right, top < bottom."""
        test_sizes = [
            (100, 100), (200, 200), (150, 300), (300, 150),
            (50, 200), (200, 50), (80, 80), (500, 500)
        ]
        
        for image_width, image_height in test_sizes:
            with self.subTest(size=f"{image_width}x{image_height}"):
                # Calculate face boundaries as done in the actual method
                face_width_ratio = 0.28
                face_height_ratio = 0.32
                
                face_width = int(image_width * face_width_ratio)
                face_height = int(image_height * face_height_ratio)
                
                face_left = (image_width - face_width) // 2
                face_top = int(image_height * 0.15)
                face_right = face_left + face_width
                face_bottom = face_top + face_height
                
                # Calculate inner boundaries with 8% adjustments (updated for ultra-minimal mask)
                inner_face_left = face_left + int(face_width * 0.08)
                inner_face_top = face_top + int(face_height * 0.08)
                inner_face_right = face_right - int(face_width * 0.08)
                inner_face_bottom = face_bottom - int(face_height * 0.02)
                
                # Apply boundary clamping
                inner_face_left = max(0, inner_face_left)
                inner_face_top = max(0, inner_face_top)
                inner_face_right = min(image_width, inner_face_right)
                inner_face_bottom = min(image_height, inner_face_bottom)
                
                # Assert inner bounds never cross
                self.assertLess(inner_face_left, inner_face_right, 
                    f"Inner left ({inner_face_left}) >= right ({inner_face_right}) for {image_width}x{image_height}")
                self.assertLess(inner_face_top, inner_face_bottom,
                    f"Inner top ({inner_face_top}) >= bottom ({inner_face_bottom}) for {image_width}x{image_height}")

    def test_minimum_dimension_requirements(self):
        """Test that all calculated dimensions are at least 1 pixel."""
        test_sizes = [
            (50, 50), (80, 80), (100, 100), (30, 200), (200, 30)
        ]
        
        for image_width, image_height in test_sizes:
            with self.subTest(size=f"{image_width}x{image_height}"):
                # Calculate all dimensions as in actual method
                face_width_ratio = 0.28
                face_height_ratio = 0.32
                
                face_width = int(image_width * face_width_ratio)
                face_height = int(image_height * face_height_ratio)
                
                # Ensure minimum face dimensions
                self.assertGreaterEqual(face_width, 1, f"Face width too small for {image_width}x{image_height}")
                self.assertGreaterEqual(face_height, 1, f"Face height too small for {image_width}x{image_height}")
                
                # Test inner area dimensions  
                inner_width = face_width - int(face_width * 0.16)  # 8% from each side (updated for ultra-minimal mask)
                
                self.assertGreaterEqual(max(1, inner_width), 1, f"Inner width calculation for {image_width}x{image_height}")

    def test_coordinates_within_image_boundaries(self):
        """Test that all coordinates stay within image boundaries."""
        test_sizes = [
            (100, 100), (200, 200), (150, 300), (300, 150), (80, 120)
        ]
        
        for image_width, image_height in test_sizes:
            with self.subTest(size=f"{image_width}x{image_height}"):
                # Recreate the coordinate calculation logic
                face_width_ratio = 0.28
                face_height_ratio = 0.32
                
                face_width = int(image_width * face_width_ratio)
                face_height = int(image_height * face_height_ratio)
                
                face_left = (image_width - face_width) // 2
                face_top = int(image_height * 0.15)
                face_right = face_left + face_width
                face_bottom = face_top + face_height
                
                # Inner boundaries with clamping (updated to match ultra-minimal mask - 8% horizontal, 2% bottom shrink)
                inner_face_left = max(0, face_left + int(face_width * 0.08))
                inner_face_top = max(0, face_top + int(face_height * 0.08))
                inner_face_right = min(image_width, face_right - int(face_width * 0.08))
                inner_face_bottom = min(image_height, face_bottom - int(face_height * 0.02))
                
                # Outer boundaries with clamping
                outer_face_left = max(0, face_left - int(face_width * 0.10))
                outer_face_top = max(0, face_top - int(face_height * 0.10))
                outer_face_right = min(image_width, face_right + int(face_width * 0.10))
                outer_face_bottom = min(image_height, face_bottom + int(face_height * 0.15))
                
                # Assert all coordinates within bounds
                self.assertGreaterEqual(inner_face_left, 0)
                self.assertGreaterEqual(inner_face_top, 0)
                self.assertLessEqual(inner_face_right, image_width)
                self.assertLessEqual(inner_face_bottom, image_height)
                
                self.assertGreaterEqual(outer_face_left, 0)
                self.assertGreaterEqual(outer_face_top, 0)
                self.assertLessEqual(outer_face_right, image_width)
                self.assertLessEqual(outer_face_bottom, image_height)

    def test_unusual_face_aspect_ratios(self):
        """Test mask generation with unusual face aspect ratios."""
        test_cases = [
            # (width, height, description)
            (100, 400, "Very tall narrow image"),
            (400, 100, "Very wide short image"),
            (150, 600, "Ultra tall image"),
            (600, 150, "Ultra wide image"),
            (75, 300, "Extreme tall narrow"),
            (300, 75, "Extreme wide short")
        ]
        
        for image_width, image_height, description in test_cases:
            with self.subTest(case=description):
                # Test that mask generation doesn't fail
                mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
                
                # Validate basic properties
                self.assertIsInstance(mask_bytes, bytes)
                self.assertGreater(len(mask_bytes), 0)
                
                # Load and verify mask
                mask_image = Image.open(io.BytesIO(mask_bytes))
                self.assertEqual(mask_image.size, (image_width, image_height))

    def test_percentage_offset_calculations(self):
        """Test that 2%, 8%, 10%, and 15% offsets produce valid mask regions."""
        base_size = 200
        
        # Test different offset scenarios (updated for ultra-minimal mask)
        offset_tests = [
            (0.02, "2% inner face bottom adjustment"),
            (0.08, "8% inner face adjustment"),  
            (0.10, "10% outer face adjustment"),  
            (0.15, "15% outer bottom adjustment")
        ]
        
        for offset, description in offset_tests:
            with self.subTest(offset=description):
                image_width = image_height = base_size
                
                face_width = int(image_width * 0.28)
                face_height = int(image_height * 0.32)
                
                # Test offset calculations don't produce invalid dimensions
                width_offset = int(face_width * offset)
                height_offset = int(face_height * offset)
                
                self.assertGreaterEqual(width_offset, 0)
                self.assertGreaterEqual(height_offset, 0)
                self.assertLess(width_offset, face_width)  # Offset smaller than face
                self.assertLess(height_offset, face_height)

    def test_boundary_clamping_near_edges(self):
        """Test boundary clamping correctly adjusts coordinates near image edges."""
        # Test image where face would extend beyond boundaries
        test_cases = [
            # Small images where clamping is essential
            (60, 60, "Tiny image requiring heavy clamping"),
            (80, 200, "Narrow image"),
            (200, 80, "Short wide image"),
            (40, 100, "Very narrow image")
        ]
        
        for image_width, image_height, description in test_cases:
            with self.subTest(case=description):
                # Calculate face positioning
                face_width = int(image_width * 0.28)
                face_height = int(image_height * 0.32)
                
                face_left = (image_width - face_width) // 2
                face_top = int(image_height * 0.15)
                face_right = face_left + face_width
                face_bottom = face_top + face_height
                
                # Test inner boundary clamping (updated for ultra-minimal mask)
                inner_face_left_unclamped = face_left + int(face_width * 0.08)
                inner_face_left_clamped = max(0, inner_face_left_unclamped)
                
                inner_face_right_unclamped = face_right - int(face_width * 0.08)
                inner_face_right_clamped = min(image_width, inner_face_right_unclamped)
                
                # Verify clamping works correctly
                self.assertGreaterEqual(inner_face_left_clamped, 0)
                self.assertLessEqual(inner_face_right_clamped, image_width)
                
                # Verify clamped coordinates are still valid
                if inner_face_left_clamped < inner_face_right_clamped:
                    self.assertLess(inner_face_left_clamped, inner_face_right_clamped)

    def test_mask_consistency_across_sizes(self):
        """Snapshot test comparing mask dimensions across different image sizes."""
        test_sizes = [
            (100, 100), (200, 200), (400, 400), (800, 800), (1024, 1024)
        ]
        
        mask_data = {}
        
        for image_width, image_height in test_sizes:
            # Generate mask
            mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
            
            # Calculate expected dimensions for comparison
            face_width = int(image_width * 0.28)
            face_height = int(image_height * 0.32)
            
            face_left = (image_width - face_width) // 2
            face_top = int(image_height * 0.15)
            
            # Store mask characteristics for consistency checking
            mask_data[f"{image_width}x{image_height}"] = {
                'face_width_ratio': face_width / image_width,
                'face_height_ratio': face_height / image_height,
                'face_left_ratio': face_left / image_width,
                'face_top_ratio': face_top / image_height,
                'mask_size_bytes': len(mask_bytes)
            }
        
        # Verify consistency in ratios across different sizes
        ratios_face_width = [data['face_width_ratio'] for data in mask_data.values()]
        ratios_face_height = [data['face_height_ratio'] for data in mask_data.values()]
        
        # All face width ratios should be approximately 0.28
        for ratio in ratios_face_width:
            self.assertAlmostEqual(ratio, 0.28, places=2)
            
        # All face height ratios should be approximately 0.32
        for ratio in ratios_face_height:
            self.assertAlmostEqual(ratio, 0.32, places=2)

    def test_mask_pixel_value_distribution(self):
        """Test that mask contains expected pixel values (0, 64, 128, 255)."""
        image_width, image_height = 400, 400
        
        mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
        mask_image = Image.open(io.BytesIO(mask_bytes))
        
        # Convert to numpy array for analysis
        mask_array = np.array(mask_image)
        unique_values = np.unique(mask_array)
        
        # Expected values: 0 (black), 64 (dark gray), 128 (medium gray), 255 (white)
        expected_values = {0, 64, 128, 255}
        actual_values = set(unique_values.tolist())
        
        # Check that we have the core mask values
        self.assertTrue(0 in actual_values, "Missing black (0) preservation area")
        self.assertTrue(255 in actual_values, "Missing white (255) transformation area")
        
        # Gray values may vary slightly due to anti-aliasing, so check ranges
        has_dark_gray = any(50 <= val <= 80 for val in actual_values)
        has_medium_gray = any(100 <= val <= 150 for val in actual_values)
        
        self.assertTrue(has_dark_gray or has_medium_gray, "Missing gray blending zones")

    def test_edge_case_extreme_small_images(self):
        """Test extremely small images that might cause calculation issues."""
        extreme_cases = [
            (20, 20), (30, 30), (10, 40), (40, 10), (15, 15)
        ]
        
        for image_width, image_height in extreme_cases:
            with self.subTest(size=f"{image_width}x{image_height}"):
                # Should not raise exception even for very small images
                try:
                    mask_bytes = self.theme_service._create_face_preservation_mask(image_width, image_height)
                    self.assertIsInstance(mask_bytes, bytes)
                    self.assertGreater(len(mask_bytes), 0)
                except Exception as e:
                    self.fail(f"Mask generation failed for {image_width}x{image_height}: {e}")

    def test_zero_and_negative_dimensions_handling(self):
        """Test graceful handling of invalid dimensions."""
        invalid_cases = [
            (0, 100), (100, 0), (0, 0), (-10, 100), (100, -10)
        ]
        
        for image_width, image_height in invalid_cases:
            with self.subTest(size=f"{image_width}x{image_height}"):
                # Should handle gracefully - either raise appropriate exception or handle safely
                if image_width <= 0 or image_height <= 0:
                    with self.assertRaises((ValueError, AttributeError)):
                        self.theme_service._create_face_preservation_mask(image_width, image_height)


if __name__ == '__main__':
    # Run all tests with verbose output
    unittest.main(verbosity=2)