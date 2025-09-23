"""
Unit Tests for AICommentGenerator
=================================

Tests for the AICommentGenerator class that handles AI-powered comment generation.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.z_ai_comment_utils import AICommentGenerator


class TestAICommentGenerator:
    """Test cases for AICommentGenerator."""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI API response."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test AI generated content"
        return mock_response
    
    @pytest.fixture
    def ai_generator_with_key(self):
        """Create AICommentGenerator with API key."""
        with patch('utils.Z_app_configurations.AppConfig.get_openai_api_key', return_value="test_api_key"):
            return AICommentGenerator(api_key="test_api_key")
    
    @pytest.fixture
    def ai_generator_no_key(self, mock_config):
        """Create AICommentGenerator without API key."""
        with patch('utils.Z_app_configurations.AppConfig.get_openai_api_key', return_value=None):
            return AICommentGenerator(api_key=None)
    
    def test_initialization_with_key(self, ai_generator_with_key):
        """Test initialization with API key."""
        assert ai_generator_with_key.api_key == "test_api_key"
        assert ai_generator_with_key.client is not None
    
    def test_initialization_without_key(self, ai_generator_no_key):
        """Test initialization without API key."""
        assert ai_generator_no_key.api_key is None
        assert ai_generator_no_key.client is None
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env_test_key'})
    def test_initialization_from_env(self):
        """Test initialization gets API key from environment."""
        ai_gen = AICommentGenerator()
        # Should get key from environment via Z_app_configurations
        assert hasattr(ai_gen, 'api_key')
    
    def test_is_available_with_client(self, ai_generator_with_key):
        """Test is_available returns True when client exists."""
        # Need to mock the client since we can't actually connect
        ai_generator_with_key.client = Mock()
        assert ai_generator_with_key.is_available() is True
    
    def test_is_available_without_client(self, ai_generator_no_key):
        """Test is_available returns False when no client."""
        # Mock client to be None to ensure test works correctly
        ai_generator_no_key.client = None
        assert ai_generator_no_key.is_available() is False
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_generate_artifact_comment_success(self, mock_openai, mock_openai_response):
        """Test successful artifact comment generation."""
        # Setup mock
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        result = ai_gen.generate_artifact_comment("customers_bronze", "bronze")
        
        assert result == "Test AI generated content"
        mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.ai
    def test_generate_artifact_comment_no_client(self, ai_generator_no_key):
        """Test artifact comment generation without client."""
        # Ensure client is None
        ai_generator_no_key.client = None
        result = ai_generator_no_key.generate_artifact_comment("test_artifact", "bronze")
        assert result == ""
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_generate_artifact_comment_api_error(self, mock_openai):
        """Test artifact comment generation with API error."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        result = ai_gen.generate_artifact_comment("test_artifact", "bronze")
        assert result == ""
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_generate_column_comment_success(self, mock_openai, mock_openai_response):
        """Test successful column comment generation."""
        # Setup mock
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        result = ai_gen.generate_column_comment("customer_id", "INT", "customers")
        
        assert result == "Test AI generated content"
        mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.ai
    def test_generate_column_comment_no_client(self, ai_generator_no_key):
        """Test column comment generation without client."""
        # Ensure client is None
        ai_generator_no_key.client = None
        result = ai_generator_no_key.generate_column_comment("test_column", "VARCHAR", "test_table")
        assert result == ""
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_generate_readable_column_name_success(self, mock_openai, mock_openai_response):
        """Test successful readable column name generation."""
        # Setup mock
        mock_client = Mock()
        mock_openai_response.choices[0].message.content = "customer_first_name"
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        result = ai_gen.generate_readable_column_name("cust_fname", "VARCHAR(50)")
        
        assert result == "customer_first_name"
        mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.ai
    def test_generate_readable_column_name_no_client(self, ai_generator_no_key):
        """Test readable column name generation without client."""
        # Ensure client is None
        ai_generator_no_key.client = None
        result = ai_generator_no_key.generate_readable_column_name("test_col", "VARCHAR")
        assert result == ""
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_generate_readable_column_name_cleanup(self, mock_openai):
        """Test that readable column name output is properly cleaned."""
        # Test various AI response formats that need cleaning
        test_cases = [
            ('"customer_first_name"', "customer_first_name"),
            ("'customer_first_name'", "customer_first_name"),
            ("Business Name: customer_first_name", "customer_first_name"),
            ("customer_first_name", "customer_first_name"),
            ("Customer Identifier", "customer_id"),  # AI might simplify to customer_id
            ("CUSTOMER_ID", "customer_id")
        ]
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        for input_response, expected_output in test_cases:
            # Setup mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = input_response
            mock_client.chat.completions.create.return_value = mock_response
            
            result = ai_gen.generate_readable_column_name("test_col", "VARCHAR")
            assert result == expected_output, f"Input: {input_response}, Expected: {expected_output}, Got: {result}"
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_length_limits(self, mock_openai):
        """Test that generated content respects length limits."""
        # Create very long mock responses
        long_artifact_comment = "A" * 200  # Longer than 120 char limit
        long_column_comment = "B" * 150    # Longer than 80 char limit
        long_column_name = "very_long_column_name_that_exceeds_fifty_characters_limit"
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        # Test artifact comment length limit (120 chars)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = long_artifact_comment
        mock_client.chat.completions.create.return_value = mock_response
        
        result = ai_gen.generate_artifact_comment("test", "bronze")
        assert len(result) <= 120
        
        # Test column comment length limit (80 chars)
        mock_response.choices[0].message.content = long_column_comment
        result = ai_gen.generate_column_comment("test", "VARCHAR", "table")
        assert len(result) <= 80
        
        # Test column name length limit (50 chars)
        mock_response.choices[0].message.content = long_column_name
        result = ai_gen.generate_readable_column_name("test", "VARCHAR")
        assert len(result) <= 50
    
    @pytest.mark.ai
    def test_parameter_validation(self, ai_generator_with_key):
        """Test parameter validation for AI generation methods."""
        # Mock client to avoid actual API calls
        ai_generator_with_key.client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test_response"
        ai_generator_with_key.client.chat.completions.create.return_value = mock_response
        
        # Test empty parameters
        result = ai_generator_with_key.generate_artifact_comment("", "")
        assert isinstance(result, str)
        
        result = ai_generator_with_key.generate_column_comment("", "", "")
        assert isinstance(result, str)
        
        result = ai_generator_with_key.generate_readable_column_name("", "")
        assert isinstance(result, str)
    
    @pytest.mark.ai
    @patch('openai.OpenAI')
    def test_prompt_construction(self, mock_openai):
        """Test that prompts are constructed correctly."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "test_response"
        mock_client.chat.completions.create.return_value = mock_response
        
        ai_gen = AICommentGenerator(api_key="test_key")
        ai_gen.client = mock_client
        
        # Test artifact comment prompt
        ai_gen.generate_artifact_comment("customers_bronze", "bronze")
        
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]['messages'][0]['content']
        
        # Verify prompt contains expected elements
        assert "customers_bronze" in prompt_content
        assert "bronze" in prompt_content
        assert "data warehouse" in prompt_content.lower()
        
        # Test column comment prompt
        ai_gen.generate_column_comment("customer_id", "INT", "customers")
        
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = call_args[1]['messages'][0]['content']
        
        assert "customer_id" in prompt_content
        assert "INT" in prompt_content
        assert "customers" in prompt_content
