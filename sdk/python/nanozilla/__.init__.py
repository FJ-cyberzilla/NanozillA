"""
NANozILLA Python SDK - Vintage 8-bit AI Image Colorization
"""

import requests
import json
from typing import List, Dict, Any
from pathlib import Path


class NanozillaClient:
    """
    Python client for NANozILLA Reactor API
    """

    def __init__(self, api_key: str, base_url: str = "https://api.nanozilla.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "NANozILLA-Python-SDK/2.0.0"
        })

    def colorize(
        self,
        image_path: str,
        style_prompt: str,
        quality: str = "high",
        safety_level: str = "block_some",
        output_format: str = "png"
    ) -> Dict[str, Any]:
        """
        Colorize a single image

        Args:
            image_path: Path to image file
            style_prompt: Style description
            quality: Image quality (high, medium, low)
            safety_level: Content safety level
            output_format: Output format (png, jpeg, webp)

        Returns:
            API response dictionary
        """
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (Path(image_path).name, image_file, 'image/jpeg')
            }
            data = {
                'style_prompt': style_prompt,
                'quality': quality,
                'safety_level': safety_level,
                'output_format': output_format
            }

            response = self.session.post(
                f"{self.base_url}/colorize",
                files=files,
                data=data
            )

        return self._handle_response(response)

    def colorize_batch(
        self,
        image_paths: List[str],
        style_prompt: str,
        concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Process multiple images in batch

        Args:
            image_paths: List of image file paths
            style_prompt: Style description for all images
            concurrent: Maximum concurrent processing

        Returns:
            Batch job response
        """
        files = []
        for image_path in image_paths:
            files.append(
                ('images[]', (Path(image_path).name, open(image_path, 'rb'), 'image/jpeg'))
            )

        data = {
            'style_prompt': style_prompt,
            'concurrent': concurrent
        }

        response = self.session.post(
            f"{self.base_url}/colorize/batch",
            files=files,
            data=data
        )

        # Close all opened files
        for _, file_tuple in files:
            file_tuple[1].close()

        return self._handle_response(response)

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a batch job

        Args:
            job_id: Job ID from batch processing

        Returns:
            Job status response
        """
        response = self.session.get(f"{self.base_url}/jobs/{job_id}")
        return self._handle_response(response)

    def get_usage_analytics(self) -> Dict[str, Any]:
        """
        Get usage statistics and analytics

        Returns:
            Analytics response
        """
        response = self.session.get(f"{self.base_url}/analytics/usage")
        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")

        if response.status_code != 200:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"API Error {response.status_code}: {error_msg}")

        if not data.get('success'):
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"API Error: {error_msg}")

        return data


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = NanozillaClient(api_key="your_api_key")

    # Colorize single image
    result = client.colorize(
        image_path="input.jpg",
        style_prompt="vibrant anime style with bright colors",
        quality="high"
    )

    print(f"Generation ID: {result['data']['generation_id']}")
    print(f"Processing Time: {result['data']['processing_time']}s")
