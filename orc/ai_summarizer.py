"""
AI Code Summarizer - Generates human-readable summaries of code

Supports multiple AI providers:
- Groq (fast, free)
- OpenAI (GPT-3.5, GPT-4)
- Ollama (local, free)
- Anthropic (Claude)
- Any custom provider

Users can configure provider via chat commands:
  /summarizer groq
  /summarizer openai
  /summarizer ollama
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional


class AICodeSummarizer:
    """Generates AI summaries for code"""
    
    def __init__(self, ai_client=None, provider=None, model=None, batch_size=10):
        """
        Initialize AI summarizer
        
        Args:
            ai_client: AI client instance (optional)
            provider: AI provider name (groq, openai, ollama, etc.)
            model: Specific model to use
            batch_size: Number of functions to batch per request
        """
        from orc.ai_client import get_ai_client
        
        # Get provider from config if not specified
        if not provider:
            try:
                from orc.config import get_config
                config = get_config()
                provider = config.get('summarizer_provider', 'groq')
            except:
                # Fallback to default if config not available
                provider = 'groq'
        
        self.provider = provider
        self.model = model
        self.ai_client = ai_client or get_ai_client(provider=provider)
        self.batch_size = batch_size
        self.batch = []
    
    def generate_summaries(self, parse_result: Dict) -> Dict:
        """
        Generate summaries for all code in parse result
        
        Args:
            parse_result: Dictionary from parser containing functions, classes, files
            
        Returns:
            Dictionary mapping target_id to summary
        """
        summaries = {}
        
        print(f"Generating AI summaries using {self.provider}...")
        
        # Summarize functions
        functions = parse_result.get('functions', {})
        if functions:
            print(f"  Summarizing {len(functions)} functions...")
            for func_id, func_data in functions.items():
                summary = self._summarize_function(
                    code=func_data.get('code', ''),
                    name=func_data.get('name', ''),
                    params=func_data.get('params', []),
                    complexity=func_data.get('complexity', 0)
                )
                if summary:
                    summary['code_hash'] = self._hash_code(func_data.get('code', ''))
                    summary['ai_model'] = f"{self.provider}/{self.model or 'default'}"
                    summaries[func_id] = summary
        
        # Summarize classes
        classes = parse_result.get('classes', {})
        if classes:
            print(f"  Summarizing {len(classes)} classes...")
            for class_id, class_data in classes.items():
                summary = self._summarize_class(
                    code=class_data.get('code', ''),
                    name=class_data.get('name', ''),
                    methods=class_data.get('methods', [])
                )
                if summary:
                    summary['code_hash'] = self._hash_code(class_data.get('code', ''))
                    summary['ai_model'] = f"{self.provider}/{self.model or 'default'}"
                    summaries[class_id] = summary
        
        # Summarize file
        files = parse_result.get('files', {})
        if files:
            print(f"  Summarizing {len(files)} files...")
            for file_path, file_data in files.items():
                summary = self._summarize_file(
                    file_path=file_path,
                    language=file_data.get('language', ''),
                    functions=functions,
                    classes=classes
                )
                if summary:
                    summaries[f"file:{file_path}"] = summary
        
        print(f"  Generated {len(summaries)} summaries")
        return summaries
    
    def _summarize_function(self, code: str, name: str, params: List, complexity: int) -> Optional[Dict]:
        """Generate summary for a single function"""
        if not code or len(code.strip()) < 10:
            return None
        
        prompt = f"""Analyze this function and provide a concise summary in JSON format.

Function: {name}
Parameters: {', '.join(params) if params else 'none'}
Complexity: {complexity}

Code:
```
{code[:1000]}  
```

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "summary_short": "One-line summary (max 80 chars)",
  "summary_detailed": "2-3 sentence explanation",
  "purpose": "Why this function exists",
  "inputs": "What it takes as input",
  "outputs": "What it returns",
  "side_effects": "Database writes, API calls, file I/O, etc. or 'none'",
  "business_rules": "Important logic/rules or 'none'",
  "edge_cases": "Special cases handled or 'none'"
}}"""
        
        try:
            response = self.ai_client.chat([
                {"role": "system", "content": "You are a code documentation expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            # Extract JSON from response
            response_text = response.strip()
            
            # Try to parse as JSON
            try:
                summary = json.loads(response_text)
                summary['confidence'] = 0.9
                return summary
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if '```json' in response_text:
                    json_start = response_text.index('```json') + 7
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.9
                    return summary
                elif '```' in response_text:
                    json_start = response_text.index('```') + 3
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.9
                    return summary
                else:
                    # Fallback: create basic summary
                    return {
                        'summary_short': f"Function: {name}",
                        'summary_detailed': f"A function named {name} with {len(params)} parameters",
                        'purpose': 'unknown',
                        'inputs': ', '.join(params) if params else 'none',
                        'outputs': 'unknown',
                        'side_effects': 'unknown',
                        'business_rules': 'unknown',
                        'edge_cases': 'unknown',
                        'confidence': 0.3
                    }
        
        except Exception as e:
            print(f"  Warning: Failed to summarize {name}: {e}")
            return None
    
    def _summarize_class(self, code: str, name: str, methods: List) -> Optional[Dict]:
        """Generate summary for a class"""
        if not code or len(code.strip()) < 10:
            return None
        
        prompt = f"""Analyze this class and provide a concise summary in JSON format.

Class: {name}
Methods: {len(methods)}

Code:
```
{code[:1000]}
```

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "summary_short": "One-line summary (max 80 chars)",
  "summary_detailed": "2-3 sentence explanation",
  "purpose": "Why this class exists",
  "key_methods": "List of main methods",
  "design_pattern": "Pattern used (if any) or 'none'",
  "dependencies": "What it depends on"
}}"""
        
        try:
            response = self.ai_client.chat([
                {"role": "system", "content": "You are a code documentation expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            # Parse response
            response_text = response.strip()
            
            try:
                summary = json.loads(response_text)
                summary['confidence'] = 0.9
                return summary
            except json.JSONDecodeError:
                # Try to extract from markdown
                if '```json' in response_text:
                    json_start = response_text.index('```json') + 7
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.9
                    return summary
                elif '```' in response_text:
                    json_start = response_text.index('```') + 3
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.9
                    return summary
                else:
                    return {
                        'summary_short': f"Class: {name}",
                        'summary_detailed': f"A class named {name} with {len(methods)} methods",
                        'purpose': 'unknown',
                        'key_methods': ', '.join(methods[:5]) if methods else 'none',
                        'design_pattern': 'unknown',
                        'dependencies': 'unknown',
                        'confidence': 0.3
                    }
        
        except Exception as e:
            print(f"  Warning: Failed to summarize class {name}: {e}")
            return None
    
    def _summarize_file(self, file_path: str, language: str, functions: Dict, classes: Dict) -> Optional[Dict]:
        """Generate summary for entire file"""
        
        # Filter functions/classes in this file
        file_functions = [f for f, data in functions.items() if data.get('file_path') == file_path]
        file_classes = [c for c, data in classes.items() if data.get('file_path') == file_path]
        
        if not file_functions and not file_classes:
            return None
        
        prompt = f"""Analyze this code file and provide a concise summary in JSON format.

File: {Path(file_path).name}
Language: {language}
Functions: {len(file_functions)}
Classes: {len(file_classes)}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "summary_short": "One-line summary of file purpose",
  "summary_detailed": "2-3 sentence explanation",
  "purpose": "Main purpose of this file",
  "main_components": "Key functions/classes",
  "architecture_role": "Role in codebase (e.g., 'API layer', 'data model', 'utility')"
}}"""
        
        try:
            response = self.ai_client.chat([
                {"role": "system", "content": "You are a code documentation expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            response_text = response.strip()
            
            try:
                summary = json.loads(response_text)
                summary['confidence'] = 0.8
                return summary
            except json.JSONDecodeError:
                if '```json' in response_text:
                    json_start = response_text.index('```json') + 7
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.8
                    return summary
                elif '```' in response_text:
                    json_start = response_text.index('```') + 3
                    json_end = response_text.index('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    summary = json.loads(json_text)
                    summary['confidence'] = 0.8
                    return summary
                else:
                    return {
                        'summary_short': f"{language} file with {len(file_functions)} functions, {len(file_classes)} classes",
                        'summary_detailed': f"Code file containing various {language} definitions",
                        'purpose': 'unknown',
                        'main_components': 'various',
                        'architecture_role': 'unknown',
                        'confidence': 0.3
                    }
        
        except Exception as e:
            print(f"  Warning: Failed to summarize file {file_path}: {e}")
            return None
    
    def _hash_code(self, code: str) -> str:
        """Generate hash of code for change detection"""
        return hashlib.md5(code.encode()).hexdigest()
