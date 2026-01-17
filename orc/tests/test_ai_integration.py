"""
ORC AI Integration Tests

Test AI client, summarizer, and tools.

Author: ORC Team
Date: 2026-01-14
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import AI components
try:
    from orc.ai.ai_client import AIClient, AIMessage, AIResponse
    from orc.ai.ai_summarizer import AICodeSummarizer
    from orc.ai.ai_tools import ORCTools, get_tools_for_ai, execute_tool
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    pytest.skip("AI components not available", allow_module_level=True)


class TestAIClient:
    """Test AI client functionality."""
    
    def test_client_initialization_groq(self):
        """Test Groq client initialization."""
        client = AIClient(provider='groq')
        assert client.provider == 'groq'
        assert client.model == 'llama-3.1-70b-versatile'
    
    def test_client_initialization_openai(self):
        """Test OpenAI client initialization."""
        client = AIClient(provider='openai', api_key='test-key')
        assert client.provider == 'openai'
        assert client.model == 'gpt-4-turbo-preview'
        assert client.api_key == 'test-key'
    
    def test_client_initialization_custom_model(self):
        """Test custom model specification."""
        client = AIClient(provider='groq', model='custom-model')
        assert client.model == 'custom-model'
    
    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(ValueError, match="Unknown provider"):
            AIClient(provider='invalid-provider')
    
    @patch('orc.ai.ai_client.requests.post')
    def test_chat_basic(self, mock_post):
        """Test basic chat functionality."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {'content': 'Hello!'},
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 5
            }
        }
        mock_post.return_value = mock_response
        
        client = AIClient(provider='groq', api_key='test')
        messages = [AIMessage(role='user', content='Hello')]
        
        response = client.chat(messages)
        
        assert response.content == 'Hello!'
        assert response.input_tokens == 10
        assert response.output_tokens == 5
    
    @patch('orc.ai.ai_client.requests.post')
    def test_chat_with_error(self, mock_post):
        """Test chat handles errors gracefully."""
        # Mock a RequestException (which is what the code catches)
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Network error")
        
        client = AIClient(provider='groq', api_key='test')
        messages = [AIMessage(role='user', content='Hello')]
        
        response = client.chat(messages)
        
        # Should return error message, not crash
        assert 'Error' in response.content
        assert response.provider == 'groq'


class TestAICodeSummarizer:
    """Test AI code summarizer."""
    
    @patch('orc.ai.ai_client.AIClient.chat')
    def test_summarize_function(self, mock_chat):
        """Test function summarization."""
        mock_chat.return_value = AIResponse(
            content="This function calculates the sum.",
            provider='groq',
            model='test'
        )
        
        summarizer = AICodeSummarizer()
        summary = summarizer.summarize_function(
            function_name='add',
            function_code='def add(a, b):\n    return a + b'
        )
        
        assert 'sum' in summary.lower()
    
    @patch('orc.ai.ai_client.AIClient.chat')
    def test_summarize_class(self, mock_chat):
        """Test class summarization."""
        mock_chat.return_value = AIResponse(
            content="This class handles user data.",
            provider='groq',
            model='test'
        )
        
        summarizer = AICodeSummarizer()
        summary = summarizer.summarize_class(
            class_name='User',
            class_code='class User:\n    pass',
            methods=['get_name', 'set_name']
        )
        
        assert 'user' in summary.lower()
    
    def test_batch_summarize_functions(self):
        """Test batch function summarization."""
        summarizer = AICodeSummarizer()
        
        functions = [
            {'name': 'func1', 'code': 'def func1(): pass'},
            {'name': 'func2', 'code': 'def func2(): pass'}
        ]
        
        # Should not crash (even if AI fails)
        summaries = summarizer.batch_summarize_functions(functions)
        
        assert isinstance(summaries, dict)
        assert len(summaries) == 2


class TestORCTools:
    """Test ORC tools for AI function calling."""
    
    def test_tool_definitions_exist(self):
        """Test tool definitions are properly formatted."""
        tools = get_tools_for_ai()
        
        assert isinstance(tools, list)
        assert len(tools) >= 10
        
        # Check first tool structure
        tool = tools[0]
        assert 'type' in tool
        assert 'function' in tool
        assert 'name' in tool['function']
        assert 'description' in tool['function']
        assert 'parameters' in tool['function']
    
    def test_orc_tools_initialization(self):
        """Test ORCTools initialization."""
        mock_db = Mock()
        tools = ORCTools(db=mock_db)
        
        assert tools.db is mock_db
    
    def test_execute_tool_query_functions(self):
        """Test tool execution."""
        mock_db = Mock()
        mock_db.query_functions.return_value = [
            {'name': 'test_func', 'complexity': 5}
        ]
        
        tools = ORCTools(db=mock_db)
        result = execute_tool('query_functions', {'pattern': 'test%'}, tools)
        
        assert isinstance(result, list)
        assert len(result) == 1
    
    def test_execute_invalid_tool(self):
        """Test executing non-existent tool."""
        mock_db = Mock()
        tools = ORCTools(db=mock_db)
        
        result = execute_tool('invalid_tool', {}, tools)
        
        assert 'Error' in str(result)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
