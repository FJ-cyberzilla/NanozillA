import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_spell_checker_import():
    """Test that spell checker can be imported"""
    try:
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import spell checker: {e}")


def test_spell_checker_initialization():
    """Test SpellChecker initialization"""
    from utils.spell_checker import SpellChecker
    checker = SpellChecker()
    assert checker is not None


def test_check_style_prompt_basic():
    """Test basic spell checking"""
    from utils.spell_checker import check_style_prompt
    prompt = "vibrant colors"
    corrected, issues = check_style_prompt(prompt)
    assert corrected == prompt
    assert issues == []
