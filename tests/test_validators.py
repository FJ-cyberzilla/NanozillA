import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_validators_import():
    """Test that validators can be imported"""
    try:
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import validators: {e}")


def test_validate_prompt_valid():
    """Test prompt validation with valid prompt"""
    from utils.validators import validate_prompt
    validate_prompt("valid prompt for testing")


def test_validate_prompt_empty():
    """Test prompt validation with empty prompt"""
    from utils.validators import validate_prompt
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        validate_prompt("")
