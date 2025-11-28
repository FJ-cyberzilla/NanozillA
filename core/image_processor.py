from PIL import Image
import io
import time
import numpy as np


class ImageProcessor:
    """Image processing utilities for NanozillA"""

    SUPPORTED_FORMATS = ['JPEG', 'JPG', 'PNG', 'WEBP', 'BMP']

    def __init__(self):
        self.processed_count = 0
        self.last_image_info = None

    def process_uploaded_image(self, uploaded_file, validate_colors=False, auto_resize=False):
        """
        Process uploaded image file

        Args:
            uploaded_file: Streamlit UploadedFile object
            validate_colors: Whether to perform color analysis
            auto_resize: Whether to automatically resize large images

        Returns:
            Tuple (image_bytes, image_info_dict)
        """
        image = Image.open(uploaded_file)
        original_format = image.format

        # Auto-resize if needed
        if auto_resize and (image.width > 2048 or image.height > 2048):
            image = self._resize_image(image, 2048)

        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Get image info
        image_info = {
            'width': image.width,
            'height': image.height,
            'format': original_format,
            'mode': image.mode,
            'file_size_mb': len(uploaded_file.getvalue()) / (1024 * 1024)
        }

        # Color analysis
        if validate_colors:
            image_info['color_analysis'] = self._analyze_colors(image)

        # Save to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        self.processed_count += 1
        self.last_image_info = image_info

        return img_byte_arr, image_info

    def prepare_for_display(self, image_bytes: bytes):
        """
        Prepare image bytes for display in Streamlit
        """
        return Image.open(io.BytesIO(image_bytes))

    def convert_format(self, image_bytes: bytes, target_format: str):
        """
        Convert image to target format
        """
        img = Image.open(io.BytesIO(image_bytes))
        target_format = target_format.upper()

        if target_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {target_format}")

        output_buffer = io.BytesIO()
        img.save(output_buffer, format=target_format)
        return output_buffer.getvalue(), {'format': target_format, 'size': len(output_buffer.getvalue())}

    def _resize_image(self, image: Image.Image, max_dim: int) -> Image.Image:
        """
        Resize image to fit within max_dim while maintaining aspect ratio
        """
        width, height = image.size
        if width > max_dim or height > max_dim:
            scaling_factor = max_dim / max(width, height)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image

    def _analyze_colors(self, image: Image.Image):
        """
        Perform basic color analysis
        """
        is_grayscale = image.mode == 'L' or (
            image.mode == 'RGB' and not np.array(image.getchannel(0)).any()
            and not np.array(image.getchannel(1)).any()
            and not np.array(image.getchannel(2)).any()
        )

        color_mode = "Grayscale" if is_grayscale else "Color"

        return {
            'is_grayscale': is_grayscale,
            'color_mode': color_mode
        }


def create_image_processor():
    """Factory function for ImageProcessor"""
    return ImageProcessor()
