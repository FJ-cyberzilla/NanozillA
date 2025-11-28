import pytest
import sys
import os
from unittest.mock import Mock, patch
from config import settings
from google import genai

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_reactor_agent_import():
    """Test that ReactorAgent can be imported"""
    try:
        # Import inside test to avoid circular imports
        from core.reactor_agent import ReactorAgent
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import ReactorAgent: {e}")


def test_create_reactor_agent():
    """Test factory function"""
    with patch('config.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_settings.MODEL_NAME = "test_model"

        with patch('google.genai.Client'):
            from core.reactor_agent import create_reactor_agent
            agent = create_reactor_agent()
            assert agent is not None


@patch('google.genai.Client')
def test_reactor_agent_initialization(mock_client):
    """Test ReactorAgent initialization"""
    with patch('config.settings') as mock_settings:
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_settings.MODEL_NAME = "test_model"

        mock_client.return_value = Mock()
        from core.reactor_agent import ReactorAgent

        agent = ReactorAgent()
        assert agent.model == "test_model"
        assert agent.generation_count == 0
