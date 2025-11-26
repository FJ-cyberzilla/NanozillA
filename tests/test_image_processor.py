import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io
from PIL import Image, UnidentifiedImageError

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.image_processor import ImageProcessor, create_image_processor


class TestImageProcessor:
    """Test suite for ImageProcessor"""
    
    @pytest.fixture
    def sample_image_file(self):
        """Create a sample image file for testing"""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    
    @pytest.fixture
    def mock_uploaded_file(self, sample_image_file):
        """Mock Streamlit uploaded file"""
        mock_file = Mock()
        mock_file.name = "test_image.png"
        mock_file.type = "image/png"
        mock_file.size = len(sample_image_file.getvalue())
        mock_file.getvalue.return_value = sample_image_file.getvalue()
        return mock_file
    
    def test_initialization(self):
        """Test ImageProcessor initialization"""
        processor = ImageProcessor()
        assert processor.processed_count == 0
        assert processor.last_image_info is None
    
    def test_supported_formats(self):
        """Test supported formats list"""
        processor = ImageProcessor()
        expected_formats = ['JPEG', 'JPG', 'PNG', 'WEBP', 'BMP']
        assert processor.SUPPORTED_FORMATS == expected_formats
    
    def test_validate_uploaded_file_valid(self, mock_uploaded_file):
        """Test file validation with valid file"""
        processor = ImageProcessor()
        
        # Should not raise any exception
        processor._validate_uploaded_file(mock_uploaded_file)
    
    def test_validate_uploaded_file_none(self):
        """Test file validation with None"""
        processor = ImageProcessor()
        
        with pytest.raises(ValueError, match="No file uploaded"):
            processor._validate_uploaded_file(None)
    
    def test_validate_uploaded_file_invalid_object(self):
        """Test file validation with invalid object"""
        processor = ImageProcessor()
        invalid_file = Mock(spec=[])  # No getvalue method
        
        with pytest.raises(ValueError, match="Invalid file object"):
            processor._validate_uploaded_file(invalid_file)
    
    def test_convert_to_bytes_success(self, mock_uploaded_file):
        """Test successful bytes conversion"""
        processor = ImageProcessor()
        result = processor._convert_to_bytes(mock_uploaded_file)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_convert_to_bytes_empty(self):
        """Test bytes conversion with empty file"""
        processor = ImageProcessor()
        empty_file = Mock()
        empty_file.getvalue.return_value = b""
        
        with pytest.raises(ValueError, match="File is empty"):
            processor._convert_to_bytes(empty_file)
    
    def test_convert_to_bytes_too_small(self):
        """Test bytes conversion with very small file"""
        processor = ImageProcessor()
        small_file = Mock()
        small_file.getvalue.return_value = b"x" * 50  # 50 bytes
        
        with pytest.raises(ValueError, match="File too small"):
            processor._convert_to_bytes(small_file)
    
    def test_convert_to_bytes_too_large(self):
        """Test bytes conversion with oversized file"""
        processor = ImageProcessor()
        large_file = Mock()
        # Create data larger than 10MB
        large_file.getvalue.return_value = b"x" * (11 * 1024 * 1024)
        
        with pytest.raises(ValueError, match="File too large"):
            processor._convert_to_bytes(large_file)
    
    def test_validate_with_pil_success(self, mock_uploaded_file):
        """Test successful PIL validation"""
        processor = ImageProcessor()
        image_bytes = mock_uploaded_file.getvalue()
        
        image, format_info = processor._validate_with_pil(image_bytes)
        
        assert isinstance(image, Image.Image)
        assert format_info['format'] == 'PNG'
        assert format_info['width'] == 100
        assert format_info['height'] == 100
    
    def test_validate_with_pil_invalid_data(self):
        """Test PIL validation with invalid image data"""
        processor = ImageProcessor()
        
        with pytest.raises(ValueError, match="Invalid image file"):
            processor._validate_with_pil(b"invalid_image_data")
    
    def test_validate_dimensions_valid(self):
        """Test dimension validation with valid dimensions"""
        processor = ImageProcessor()
        image = Image.new('RGB', (500, 500))
        
        # Should not raise any exception
        processor._validate_dimensions(image, auto_resize=True)
    
    def test_validate_dimensions_too_small(self):
        """Test dimension validation with too small image"""
        processor = ImageProcessor()
        image = Image.new('RGB', (10, 10))  # Below minimum
        
        with pytest.raises(ValueError, match="Image too small"):
            processor._validate_dimensions(image, auto_resize=True)
    
    def test_analyze_colors_rgb(self):
        """Test color analysis with RGB image"""
        processor = ImageProcessor()
        image = Image.new('RGB', (100, 100), color=(255, 0, 0))  # Red image
        
        color_info = processor._analyze_colors(image)
        
        assert color_info['color_mode'] == 'RGB'
        assert color_info['average_rgb'] == [255, 0, 0]  # Should be red
        assert color_info['is_grayscale'] is False  # Red is not grayscale
    
    def test_analyze_colors_grayscale(self):
        """Test color analysis with grayscale image"""
        processor = ImageProcessor()
        image = Image.new('L', (100, 100), color=128)  # Grayscale
        
        color_info = processor._analyze_colors(image)
        
        # Image should be converted to RGB for analysis
        assert color_info['color_mode'] == 'RGB'
        # Grayscale should have similar RGB values
        assert color_info['is_grayscale'] is True
    
    def test_get_image_info(self, mock_uploaded_file):
        """Test comprehensive image info generation"""
        processor = ImageProcessor()
        image = Image.new('RGB', (200, 150))
        
        info = processor._get_image_info(
            image=image,
            uploaded_file=mock_uploaded_file,
            format_info={'format': 'PNG', 'mode': 'RGB'}
        )
        
        expected_keys = [
            'filename', 'format', 'mode', 'width', 'height',
            'aspect_ratio', 'file_size_bytes', 'file_size_mb',
            'total_pixels', 'has_transparency', 'is_animated'
        ]
        
        for key in expected_keys:
            assert key in info
        
        assert info['width'] == 200
        assert info['height'] == 150
        assert info['aspect_ratio'] == pytest.approx(200/150, 0.01)
        assert info['total_pixels'] == 30000
    
    def test_prepare_for_display_success(self, mock_uploaded_file):
        """Test successful display preparation"""
        processor = ImageProcessor()
        image_bytes = mock_uploaded_file.getvalue()
        
        result = processor.prepare_for_display(image_bytes)
        
        assert isinstance(result, Image.Image)
    
    def test_prepare_for_display_empty(self):
        """Test display preparation with empty data"""
        processor = ImageProcessor()
        
        result = processor.prepare_for_display(b"")
        
        assert result is None
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        processor = ImageProcessor()
        stats = processor.get_stats()
        
        expected_keys = [
            'processed_count', 'last_image_info',
            'supported_formats', 'max_dimension', 'max_file_size_mb'
        ]
        
        for key in expected_keys:
            assert key in stats


class TestImageProcessorIntegration:
    """Integration tests for ImageProcessor"""
    
    @pytest.fixture
    def sample_images(self):
        """Create multiple sample images for testing"""
        images = []
        sizes = [(100, 100), (200, 150), (300, 200)]
        colors = ['red', 'green', 'blue']
        
        for size, color in zip(sizes, colors):
            image = Image.new('RGB', size, color=color)
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            mock_file = Mock()
            mock_file.name = f"test_{color}.png"
            mock_file.type = "image/png"
            mock_file.size = len(buffer.getvalue())
            mock_file.getvalue.return_value = buffer.getvalue()
            
            images.append(mock_file)
        
        return images
    
    def test_process_uploaded_image_success(self, mock_uploaded_file):
        """Test successful image processing"""
        processor = ImageProcessor()
        
        image_bytes, image_info = processor.process_uploaded_image(
            mock_uploaded_file,
            validate_colors=True,
            auto_resize=True
        )
        
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0
        assert image_info['filename'] == "test_image.png"
        assert image_info['format'] == 'PNG'
        assert processor.processed_count == 1
    
    def test_process_uploaded_image_invalid_file(self):
        """Test processing with invalid file"""
        processor = ImageProcessor()
        invalid_file = Mock()
        invalid_file.getvalue.return_value = b"invalid_data"
        
        with pytest.raises(ValueError):
            processor.process_uploaded_image(invalid_file)
    
    def test_create_image_processor(self):
        """Test factory function"""
        processor = create_image_processor()
        assert isinstance(processor, ImageProcessor)
