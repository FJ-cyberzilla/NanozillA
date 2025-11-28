from config.settings import settings


def validate_image(uploaded_file):
    """Validate uploaded image file"""
    if uploaded_file is None:
        raise ValueError("No file uploaded")

    if uploaded_file.size > settings.MAX_IMAGE_SIZE:
        raise ValueError(f"File too large. Max size: {settings.MAX_IMAGE_SIZE // (1024*1024)}MB")

    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    if uploaded_file.type not in allowed_types:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(allowed_types)}")


def validate_prompt(prompt):
    """Validate style prompt"""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        raise ValueError(f"Prompt too long. Max {settings.MAX_PROMPT_LENGTH} characters")
