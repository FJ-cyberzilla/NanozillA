import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io
from PIL import Image
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import io
from PIL import Image

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanozilla_reactor.core.reactor_agent import ReactorAgent, create_reactor_agent
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reactor_agent import ReactorAgent, create_reactor_agent


class TestReactorAgent:
    """Test suite for ReactorAgent"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch('core.reactor_agent.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = "test_api_key"
            mock_settings.MODEL_NAME = "test-model"
            mock_settings.MAX_PROMPT_LENGTH = 2000
            yield mock_settings
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes for testing"""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def test_initialization_success(self, mock_settings):
        """Test successful ReactorAgent initialization"""
        with patch('core.reactor_agent.genai.Client') as mock_client:
            mock_client.return_value = Mock()
            agent = ReactorAgent()
            
            assert agent.model == "test-model"
            assert agent.generation_count == 0
            assert agent.last_generation_time is None
    
    def test_initialization_missing_api_key(self):
        """Test initialization with missing API key"""
        with patch('core.reactor_agent.settings') as mock_settings:
            mock_settings.GEMINI_API_KEY = None
            mock_settings.MODEL_NAME = "test-model"
            
            with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
                ReactorAgent()
    
    def test_validate_inputs_valid(self, mock_settings):
        """Test input validation with valid inputs"""
        with patch('core.reactor_agent.genai.Client'):
            agent = ReactorAgent()
            image_bytes = b"fake_image_data" * 10  # 140 bytes
            
            # Should not raise any exception
            agent._validate_inputs(image_bytes, "valid style prompt")
    
    def test_validate_inputs_invalid_image(self, mock_settings):
        """Test input validation with invalid image"""
        with patch('core.reactor_agent.genai.Client'):
            agent = ReactorAgent()
            
            with pytest.raises(ValueError, match="Invalid image data"):
                agent._validate_inputs(b"", "valid style prompt")
    
    def test_validate_inputs_invalid_prompt(self, mock_settings):
        """Test input validation with invalid prompt"""
        with patch('core.reactor_agent.genai.Client'):
            agent = ReactorAgent()
            image_bytes = b"fake_image_data" * 10
            
            with pytest.raises(ValueError, match="Style prompt cannot be empty"):
                agent._validate_inputs(image_bytes, "")
    
    def test_prepare_config_default(self, mock_settings):
        """Test configuration preparation with default values"""
        with patch('core.reactor_agent.genai.Client'):
            agent = ReactorAgent()
            config = agent._prepare_config("high", "block_some")
            
            assert config["number_of_images"] == 1
            assert config["quality"] == "high"
            assert config["safety_filter_level"] == "block_some"
    
    def test_prepare_config_invalid_quality(self, mock_settings):
        """Test configuration preparation with invalid quality"""
        with patch('core.reactor_agent.genai.Client'):
            agent = ReactorAgent()
            config = agent._prepare_config("invalid", "block_some")
            
            # Should default to "high"
            assert config["quality"] == "high"
    
    @patch('core.reactor_agent.genai.Client')
    def test_is_fatal_error_detection(self, mock_client, mock_settings):
        """Test fatal error detection"""
        agent = ReactorAgent()
        
        # Test fatal errors
        fatal_errors = [
            "invalid api key provided",
            "authentication failed",
            "quota exceeded for this model",
            "model not found in catalog",
            "permission denied for this resource",
            "content policy violation detected"
        ]
        
        for error_msg in fatal_errors:
            error = Exception(error_msg)
            assert agent._is_fatal_api_error(error) is True
    
    @patch('core.reactor_agent.genai.Client')
    def test_is_fatal_error_non_fatal(self, mock_client, mock_settings):
        """Test non-fatal error detection"""
        agent = ReactorAgent()
        
        non_fatal_errors = [
            "temporary service issue",
            "network timeout",
            "rate limit exceeded temporarily",
            "internal server error"
        ]
        
        for error_msg in non_fatal_errors:
            error = Exception(error_msg)
            assert agent._is_fatal_api_error(error) is False
    
    def test_create_reactor_agent_with_fallback(self, mock_settings):
        """Test factory function with fallback"""
        with patch('core.reactor_agent.genai.Client') as mock_client:
            mock_client.return_value = Mock()
            agent = create_reactor_agent()
            
            assert agent is not None
            assert isinstance(agent, ReactorAgent)


class TestReactorAgentIntegration:
    """Integration tests for ReactorAgent"""
    
    @pytest.fixture
    def sample_image_data(self):
        """Generate sample image data"""
        image = Image.new('RGB', (50, 50), color='blue')
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @patch('core.reactor_agent.genai.Client')
    def test_execute_colorization_success(self, mock_client, mock_settings, sample_image_data):
        """Test successful colorization execution"""
        # Mock the API response
        mock_response = Mock()
        mock_generated_image = Mock()
        mock_generated_image.image.image_bytes = sample_image_data
        mock_response.generated_images = [mock_generated_image]
        
        mock_client_instance = Mock()
        mock_client_instance.models.generate_images.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        agent = ReactorAgent()
        result = agent.execute_colorization(
            image_bytes=sample_image_data,
            style_prompt="test style",
            retry_attempts=1
        )
        
        assert result == sample_image_data
        assert agent.generation_count == 1
        assert agent.last_generation_time is not None
    
    @patch('core.reactor_agent.genai.Client')
    def test_execute_colorization_retry_logic(self, mock_client, mock_settings, sample_image_data):
        """Test retry logic on API failure"""
        mock_client_instance = Mock()
        # First call fails, second succeeds
        mock_client_instance.models.generate_images.side_effect = [
            Exception("Temporary error"),
            Mock(generated_images=[Mock(image=Mock(image_bytes=sample_image_data))])
        ]
        mock_client.return_value = mock_client_instance
        
        agent = ReactorAgent()
        result = agent.execute_colorization(
            image_bytes=sample_image_data,
            style_prompt="test style", 
            retry_attempts=2
        )
        
        assert result == sample_image_data
        assert mock_client_instance.models.generate_images.call_count == 2
    
    @patch('core.reactor_agent.genai.Client')
    def test_get_stats(self, mock_client, mock_settings):
        """Test statistics retrieval"""
        agent = ReactorAgent()
        stats = agent.get_stats()
        
        expected_keys = [
            "generation_count", 
            "last_generation_time",
            "total_processing_time", 
            "average_generation_time",
            "model", 
            "status"
        ]
        
        for key in expected_keys:
            assert key in stats
        assert stats["status"] == "ready"
