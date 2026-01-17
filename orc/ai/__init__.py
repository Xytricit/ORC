"""
ORC AI Integration Module

Provides AI client abstraction, code summarization, and tool definitions
for AI-powered code analysis.

Author: ORC Team
Date: 2026-01-14
"""

from orc.ai.ai_client import AIClient
from orc.ai.ai_summarizer import AICodeSummarizer
from orc.ai.ai_tools import ORCTools, get_tools_for_ai
from orc.ai.ai_backend import AIBackend, create_ai_backend

__all__ = [
    'AIClient',
    'AICodeSummarizer',
    'ORCTools',
    'get_tools_for_ai',
    'AIBackend',
    'create_ai_backend',
]
