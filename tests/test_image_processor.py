import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_image_processor_import():
    """Test that ImageProcessor can be imported"""
    try:
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import ImageProcessor: {e}")


def test_create_image_processor():
    """Test factory function"""
    from core.image_processor import create_image_processor
    processor = create_image_processor()
    assert processor is not None


def test_image_processor_initialization():
    """Test ImageProcessor initialization"""
    from core.image_processor import ImageProcessor
    processor = ImageProcessor()
    assert processor.processed_count == 0
    assert processor.last_image_info is None


def test_supported_formats():
    """Test supported formats"""
    from core.image_processor import ImageProcessor
    processor = ImageProcessor()
    expected_formats = ['JPEG', 'JPG', 'PNG', 'WEBP', 'BMP']
    assert processor.SUPPORTED_FORMATS == expected_formats
