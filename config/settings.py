import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "imagen-3.0-generate-002")

    # Image Processing Limits
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DIMENSION = 4096
    MIN_DIMENSION = 32

    # Generation Settings
    MAX_PROMPT_LENGTH = 2000
    DEFAULT_QUALITY = "high"
    DEFAULT_SAFETY_LEVEL = "block_some"

    # Validation
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")


settings = Settings()
