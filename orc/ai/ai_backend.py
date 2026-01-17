"""
ORC AI Backend Intelligence Layer

Adds semantic meaning to raw parser data.
Runs after parsing, before storage.

Author: ORC Team
Date: 2026-01-17
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from orc.ai.ai_client import AIClient, AIMessage
from orc.ai.ai_summarizer import AICodeSummarizer

logger = logging.getLogger(__name__)


class AIBackend:
    """
    AI Backend Intelligence Layer.
    
    Takes raw parser output and adds semantic intelligence:
    - Purpose/description
    - Business logic explanation
    - Risk assessment
    - Performance implications
    
    NO HALLUCINATION - Only extracts facts from code.
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        """
        Initialize AI Backend.
        
        Args:
            ai_client: AIClient instance (creates new if None)
        """
        self.ai_client = ai_client or AIClient(provider='groq')
        self.summarizer = AICodeSummarizer(ai_client=self.ai_client)
    
    def enhance_parser_output(self, parser_result: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        Enhance raw parser output with AI intelligence.
        
        Args:
            parser_result: Raw output from parser
            file_path: Path to source file
        
        Returns:
            Enhanced parser result with AI insights
        """
        enhanced = parser_result.copy()
        
        # Enhance functions
        if 'functions' in parser_result:
            enhanced['functions'] = self._enhance_functions(
                parser_result['functions'], 
                file_path
            )
        
        # Enhance classes
        if 'classes' in parser_result:
            enhanced['classes'] = self._enhance_classes(
                parser_result['classes'],
                file_path
            )
        
        # Add module-level insights
        enhanced['module_insights'] = self._analyze_module(parser_result, file_path)
        
        return enhanced
    
    def _enhance_functions(self, functions: Dict[str, Dict], file_path: Path) -> Dict[str, Dict]:
        """Enhance function data with AI insights."""
        enhanced_functions = {}
        
        for func_id, func_data in functions.items():
            enhanced_func = func_data.copy()
            
            try:
                # Generate purpose from code
                if func_data.get('code'):
                    purpose = self._extract_function_purpose(
                        func_data['name'],
                        func_data['code'],
                        func_data
                    )
                    enhanced_func['purpose'] = purpose
                
                # Assess risk level
                enhanced_func['risk_level'] = self._assess_function_risk(func_data)
                
                # Analyze performance
                enhanced_func['performance_notes'] = self._analyze_performance(func_data)
                
                enhanced_functions[func_id] = enhanced_func
                
            except Exception as e:
                logger.error(f"Failed to enhance function {func_data['name']}: {e}")
                enhanced_functions[func_id] = func_data
        
        return enhanced_functions
    
    def _enhance_classes(self, classes: Dict[str, Dict], file_path: Path) -> Dict[str, Dict]:
        """Enhance class data with AI insights."""
        enhanced_classes = {}
        
        for class_id, class_data in classes.items():
            enhanced_class = class_data.copy()
            
            try:
                # Determine class purpose
                purpose = self._extract_class_purpose(class_data)
                enhanced_class['purpose'] = purpose
                
                # Assess complexity
                enhanced_class['complexity_note'] = self._assess_class_complexity(class_data)
                
                enhanced_classes[class_id] = enhanced_class
                
            except Exception as e:
                logger.error(f"Failed to enhance class {class_data['name']}: {e}")
                enhanced_classes[class_id] = class_data
        
        return enhanced_classes
    
    def _extract_function_purpose(self, name: str, code: str, metadata: Dict) -> str:
        """Extract function purpose using AI (brief, factual)."""
        # Build context from metadata
        context_parts = []
        
        if metadata.get('decorators'):
            context_parts.append(f"Decorators: {', '.join(metadata['decorators'])}")
        
        if metadata.get('parameters'):
            context_parts.append(f"Parameters: {', '.join(metadata['parameters'])}")
        
        if metadata.get('calls'):
            context_parts.append(f"Calls: {', '.join(metadata['calls'][:5])}")
        
        context = " | ".join(context_parts) if context_parts else None
        
        # Use summarizer for brief purpose (under 100 words)
        try:
            summary = self.summarizer.summarize_function(name, code, context)
            return summary
        except Exception as e:
            logger.error(f"Failed to extract purpose for {name}: {e}")
            return f"Function: {name}"
    
    def _extract_class_purpose(self, class_data: Dict) -> str:
        """Extract class purpose from metadata."""
        name = class_data['name']
        methods = class_data.get('methods', [])
        base_classes = class_data.get('base_classes', [])
        
        # Simple heuristic-based purpose
        if any(base in ['BaseModel', 'Model', 'Schema'] for base in base_classes):
            return f"Data model: {name}"
        elif any(method in methods for method in ['get', 'post', 'put', 'delete']):
            return f"API handler: {name}"
        elif 'Service' in name:
            return f"Business logic service: {name}"
        elif 'Manager' in name:
            return f"Resource manager: {name}"
        else:
            return f"Class: {name} with {len(methods)} methods"
    
    def _assess_function_risk(self, func_data: Dict) -> str:
        """Assess function risk level based on metadata."""
        complexity = func_data.get('complexity', 1)
        calls = func_data.get('calls', [])
        
        # High risk indicators
        if complexity > 20:
            return 'high'
        elif complexity > 10:
            return 'medium'
        elif len(calls) > 10:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_performance(self, func_data: Dict) -> str:
        """Analyze function performance characteristics."""
        complexity = func_data.get('complexity', 1)
        calls = func_data.get('calls', [])
        is_async = func_data.get('is_async', False)
        
        notes = []
        
        if complexity > 15:
            notes.append(f"High complexity ({complexity})")
        
        if len(calls) > 15:
            notes.append(f"Many function calls ({len(calls)})")
        
        if is_async:
            notes.append("Async function")
        
        return ' | '.join(notes) if notes else 'Normal'
    
    def _assess_class_complexity(self, class_data: Dict) -> str:
        """Assess class complexity."""
        methods = class_data.get('methods', [])
        base_classes = class_data.get('base_classes', [])
        
        if len(methods) > 20:
            return f"Large class ({len(methods)} methods)"
        elif len(methods) > 10:
            return f"Medium class ({len(methods)} methods)"
        elif len(base_classes) > 2:
            return f"Complex inheritance ({len(base_classes)} base classes)"
        else:
            return "Normal"
    
    def _analyze_module(self, parser_result: Dict, file_path: Path) -> Dict[str, Any]:
        """Generate module-level insights."""
        insights = {
            'file_type': self._detect_file_type(parser_result),
            'complexity_summary': self._summarize_complexity(parser_result),
            'security_notes': self._security_notes(parser_result),
            'recommendations': self._generate_recommendations(parser_result)
        }
        
        return insights
    
    def _detect_file_type(self, parser_result: Dict) -> str:
        """Detect file type/purpose."""
        # Check for API endpoints
        if parser_result.get('api_endpoints'):
            return 'api_handler'
        
        # Check for data models
        if parser_result.get('data_models'):
            return 'data_model'
        
        # Check for tests
        functions = parser_result.get('functions', {})
        if any('test_' in f['name'] for f in functions.values()):
            return 'test_file'
        
        # Check for config
        if parser_result.get('configuration', {}).get('env_vars'):
            return 'configuration'
        
        return 'source_file'
    
    def _summarize_complexity(self, parser_result: Dict) -> str:
        """Summarize overall complexity."""
        functions = parser_result.get('functions', {})
        classes = parser_result.get('classes', {})
        
        if not functions and not classes:
            return "Empty or minimal file"
        
        avg_complexity = sum(f.get('complexity', 1) for f in functions.values()) / max(len(functions), 1)
        
        if avg_complexity > 15:
            return "High complexity"
        elif avg_complexity > 8:
            return "Medium complexity"
        else:
            return "Low complexity"
    
    def _security_notes(self, parser_result: Dict) -> List[str]:
        """Extract security-related notes."""
        notes = []
        
        security = parser_result.get('security', {})
        
        if security.get('sql_injection_risks'):
            notes.append(f"{len(security['sql_injection_risks'])} SQL injection risks")
        
        if security.get('secrets'):
            notes.append(f"{len(security['secrets'])} hardcoded secrets")
        
        return notes
    
    def _generate_recommendations(self, parser_result: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for high complexity functions
        functions = parser_result.get('functions', {})
        complex_funcs = [f for f in functions.values() if f.get('complexity', 1) > 15]
        if complex_funcs:
            recommendations.append(f"Refactor {len(complex_funcs)} complex function(s)")
        
        # Check for security issues
        security = parser_result.get('security', {})
        if security.get('sql_injection_risks'):
            recommendations.append("Fix SQL injection vulnerabilities")
        
        # Check for missing error handling
        error_handling = parser_result.get('error_handling', {})
        if not error_handling.get('try_blocks') and len(functions) > 5:
            recommendations.append("Add error handling")
        
        return recommendations


def create_ai_backend(provider: str = 'groq') -> AIBackend:
    """
    Create AI Backend with sensible defaults.
    
    Args:
        provider: AI provider name
    
    Returns:
        AIBackend instance
    """
    client = AIClient(provider=provider)
    return AIBackend(ai_client=client)
