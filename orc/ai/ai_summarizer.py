"""
ORC AI Code Summarizer

Generates AI-powered summaries for functions, classes, and modules.

Author: ORC Team
Date: 2026-01-14
"""

from typing import Dict, List, Optional
import logging

from orc.ai.ai_client import AIClient, AIMessage

logger = logging.getLogger(__name__)


class AICodeSummarizer:
    """
    AI-powered code summarization.
    
    Generates natural language summaries of code entities.
    """
    
    # System prompts for different entity types
    SYSTEM_PROMPTS = {
        'function': """You are a code documentation expert. 
Generate a concise, clear summary of what the given function does.
Focus on: purpose, parameters, return value, and key behavior.
Keep it under 100 words.""",
        
        'class': """You are a code documentation expert.
Generate a concise, clear summary of what the given class does.
Focus on: purpose, key methods, and responsibilities.
Keep it under 150 words.""",
        
        'module': """You are a code documentation expert.
Generate a concise, clear summary of what the given module does.
Focus on: main purpose, key exports, and how it fits in the codebase.
Keep it under 200 words.""",
    }
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        """
        Initialize summarizer.
        
        Args:
            ai_client: AIClient instance (creates new if None)
        """
        self.ai_client = ai_client or AIClient(provider='groq')
    
    def summarize_function(
        self,
        function_name: str,
        function_code: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate summary for a function.
        
        Args:
            function_name: Function name
            function_code: Full function source code
            context: Additional context (file name, class name, etc.)
        
        Returns:
            str: Generated summary
        """
        prompt = f"Function: {function_name}\n\n"
        if context:
            prompt += f"Context: {context}\n\n"
        prompt += f"Code:\n```python\n{function_code}\n```"
        
        return self._generate_summary('function', prompt)
    
    def summarize_class(
        self,
        class_name: str,
        class_code: str,
        methods: Optional[List[str]] = None
    ) -> str:
        """
        Generate summary for a class.
        
        Args:
            class_name: Class name
            class_code: Full class source code
            methods: List of method names
        
        Returns:
            str: Generated summary
        """
        prompt = f"Class: {class_name}\n\n"
        if methods:
            prompt += f"Methods: {', '.join(methods)}\n\n"
        prompt += f"Code:\n```python\n{class_code}\n```"
        
        return self._generate_summary('class', prompt)
    
    def summarize_module(
        self,
        module_path: str,
        imports: List[str],
        exports: List[str],
        functions: List[str],
        classes: List[str]
    ) -> str:
        """
        Generate summary for a module.
        
        Args:
            module_path: Path to module file
            imports: List of imported modules
            exports: List of exported entities
            functions: List of function names
            classes: List of class names
        
        Returns:
            str: Generated summary
        """
        prompt = f"Module: {module_path}\n\n"
        prompt += f"Imports: {', '.join(imports[:10])}\n"
        prompt += f"Exports: {', '.join(exports)}\n"
        prompt += f"Functions: {', '.join(functions)}\n"
        prompt += f"Classes: {', '.join(classes)}\n"
        
        return self._generate_summary('module', prompt)
    
    def batch_summarize_functions(
        self,
        functions: List[Dict]
    ) -> Dict[str, str]:
        """
        Summarize multiple functions.
        
        Args:
            functions: List of dicts with 'name' and 'code'
        
        Returns:
            dict: Mapping of function_id to summary
        """
        summaries = {}
        
        for func in functions:
            func_id = func.get('func_id') or func['name']
            try:
                summary = self.summarize_function(
                    function_name=func['name'],
                    function_code=func.get('code', ''),
                    context=func.get('file', '')
                )
                summaries[func_id] = summary
            except Exception as e:
                logger.error(f"Failed to summarize {func['name']}: {e}")
                summaries[func_id] = f"Error: {str(e)}"
        
        return summaries
    
    def _generate_summary(self, entity_type: str, prompt: str) -> str:
        """
        Generate summary using AI.
        
        Args:
            entity_type: Type of entity ('function', 'class', 'module')
            prompt: Prompt text
        
        Returns:
            str: Generated summary
        """
        system_prompt = self.SYSTEM_PROMPTS.get(entity_type, self.SYSTEM_PROMPTS['function'])
        
        messages = [
            AIMessage(role='system', content=system_prompt),
            AIMessage(role='user', content=prompt)
        ]
        
        try:
            response = self.ai_client.chat(messages)
            return response.content.strip()
        
        except Exception as e:
            logger.error(f"AI summarization failed: {e}")
            return f"Error generating summary: {str(e)}"
    
    def summarize_with_caching(
        self,
        entity_id: str,
        entity_type: str,
        code: str,
        cache_db = None
    ) -> str:
        """
        Generate summary with database caching.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            code: Source code
            cache_db: GraphDB instance for caching
        
        Returns:
            str: Summary (from cache or newly generated)
        """
        # Check cache
        if cache_db:
            cached = cache_db.get_summary(entity_id, entity_type)
            if cached:
                return cached
        
        # Generate new summary
        if entity_type == 'function':
            summary = self.summarize_function(entity_id, code)
        elif entity_type == 'class':
            summary = self.summarize_class(entity_id, code)
        else:
            summary = f"Summary for {entity_type}: {entity_id}"
        
        # Store in cache
        if cache_db:
            cache_db.store_summary(
                entity_id=entity_id,
                entity_type=entity_type,
                summary=summary,
                provider=self.ai_client.provider
            )
        
        return summary


# Convenience function
def create_summarizer(provider: str = 'groq', **kwargs) -> AICodeSummarizer:
    """
    Create AI summarizer with sensible defaults.
    
    Args:
        provider: AI provider name
        **kwargs: Additional arguments for AIClient
    
    Returns:
        AICodeSummarizer instance
    """
    client = AIClient(provider=provider, **kwargs)
    return AICodeSummarizer(ai_client=client)
