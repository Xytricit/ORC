"""
Tests for ORC Onboarding System
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from orc.cli.onboarding import ORCOnboarding, run_onboarding_if_needed


class TestORCOnboarding:
    """Test the onboarding flow"""
    
    def test_onboarding_initialization(self, tmp_path):
        """Test onboarding initializes correctly"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            
            assert onboarding.config_dir == tmp_path / ".orc"
            assert onboarding.env_file == tmp_path / ".orc" / ".env"
    
    def test_needs_onboarding_no_env_file(self, tmp_path):
        """Test needs_onboarding returns True when no .env exists"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            
            assert onboarding.needs_onboarding() is True
    
    def test_needs_onboarding_empty_env_file(self, tmp_path):
        """Test needs_onboarding returns True with empty .env"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            onboarding.config_dir.mkdir(parents=True, exist_ok=True)
            onboarding.env_file.write_text("")
            
            assert onboarding.needs_onboarding() is True
    
    def test_needs_onboarding_with_api_key(self, tmp_path):
        """Test needs_onboarding returns False with valid config"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            onboarding.config_dir.mkdir(parents=True, exist_ok=True)
            onboarding.env_file.write_text("GROQ_API_KEY=test_key_1234567890")
            
            assert onboarding.needs_onboarding() is False
    
    @patch('orc.cli.onboarding.Prompt.ask')
    @patch('orc.cli.onboarding.Console')
    def test_choose_provider_groq(self, mock_console, mock_prompt, tmp_path):
        """Test choosing Groq provider"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            mock_prompt.return_value = 'groq'
            
            onboarding = ORCOnboarding()
            provider = onboarding._choose_provider()
            
            assert provider == 'groq'
            assert mock_prompt.called
    
    @patch('orc.cli.onboarding.Prompt.ask')
    @patch('orc.cli.onboarding.Console')
    def test_choose_provider_openai(self, mock_console, mock_prompt, tmp_path):
        """Test choosing OpenAI provider"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            mock_prompt.return_value = 'openai'
            
            onboarding = ORCOnboarding()
            provider = onboarding._choose_provider()
            
            assert provider == 'openai'
    
    @patch('orc.cli.onboarding.Prompt.ask')
    @patch('orc.cli.onboarding.Console')
    def test_get_api_key_normal(self, mock_console, mock_prompt, tmp_path):
        """Test getting API key for normal provider"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            mock_prompt.return_value = 'test_api_key_12345'
            
            onboarding = ORCOnboarding()
            api_key = onboarding._get_api_key('groq')
            
            assert api_key == 'test_api_key_12345'
            # Verify password=True was used (hidden input)
            assert mock_prompt.call_args[1].get('password') is True
    
    @patch('orc.cli.onboarding.Console')
    def test_get_api_key_ollama(self, mock_console, tmp_path):
        """Test getting API key for Ollama (none needed)"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            api_key = onboarding._get_api_key('ollama')
            
            assert api_key is None
    
    def test_save_config_groq(self, tmp_path):
        """Test saving Groq configuration"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            onboarding._save_config('groq', 'test_key_123')
            
            # Check file created
            assert onboarding.env_file.exists()
            
            # Check content
            content = onboarding.env_file.read_text()
            assert 'ORC_AI_PROVIDER=groq' in content
            assert 'GROQ_API_KEY=test_key_123' in content
    
    def test_save_config_ollama_no_key(self, tmp_path):
        """Test saving Ollama config (no API key)"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            onboarding._save_config('ollama', None)
            
            # Check file created
            assert onboarding.env_file.exists()
            
            # Check content
            content = onboarding.env_file.read_text()
            assert 'ORC_AI_PROVIDER=ollama' in content
            assert 'API_KEY' not in content
    
    def test_save_config_creates_directory(self, tmp_path):
        """Test config saving creates directory if needed"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            
            # Directory shouldn't exist yet
            assert not onboarding.config_dir.exists()
            
            onboarding._save_config('groq', 'key123')
            
            # Directory should be created
            assert onboarding.config_dir.exists()
            assert onboarding.env_file.exists()
    
    @patch('orc.cli.onboarding.Console')
    def test_show_token_usage(self, mock_console, tmp_path):
        """Test token usage display"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            
            # Should not raise exception
            onboarding.show_token_usage(100, 50, 'groq')
            
            # Console should be used
            assert mock_console.called
    
    @patch('orc.cli.onboarding.Console')
    def test_show_token_usage_with_cost(self, mock_console, tmp_path):
        """Test token usage display with cost calculation"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            onboarding = ORCOnboarding()
            
            # OpenAI should show cost
            onboarding.show_token_usage(1000, 500, 'openai')
            
            # Console should be used
            assert mock_console.called
    
    @patch('orc.cli.onboarding.Prompt.ask')
    @patch('orc.cli.onboarding.Console')
    def test_full_onboarding_run(self, mock_console, mock_prompt, tmp_path):
        """Test complete onboarding flow"""
        with patch('orc.cli.onboarding.Path.home', return_value=tmp_path):
            # Mock user inputs
            mock_prompt.side_effect = ['groq', 'test_key_12345']
            
            onboarding = ORCOnboarding()
            result = onboarding.run()
            
            # Check return value
            assert result['provider'] == 'groq'
            assert result['api_key'] == 'test_key_12345'
            
            # Check file saved
            assert onboarding.env_file.exists()
            content = onboarding.env_file.read_text()
            assert 'GROQ_API_KEY=test_key_12345' in content
    
    @patch('orc.cli.onboarding.ORCOnboarding')
    def test_run_onboarding_if_needed_runs(self, mock_onboarding_class, tmp_path):
        """Test run_onboarding_if_needed runs when needed"""
        mock_instance = MagicMock()
        mock_instance.needs_onboarding.return_value = True
        mock_onboarding_class.return_value = mock_instance
        
        result = run_onboarding_if_needed()
        
        assert result is True
        assert mock_instance.run.called
    
    @patch('orc.cli.onboarding.ORCOnboarding')
    def test_run_onboarding_if_needed_skips(self, mock_onboarding_class, tmp_path):
        """Test run_onboarding_if_needed skips when not needed"""
        mock_instance = MagicMock()
        mock_instance.needs_onboarding.return_value = False
        mock_onboarding_class.return_value = mock_instance
        
        result = run_onboarding_if_needed()
        
        assert result is False
        assert not mock_instance.run.called
