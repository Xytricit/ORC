"""React/JSX parser with full support for React-specific features.

Extracts:
- Function components (with and without props)
- Class components (with lifecycle methods)
- React Hooks (useState, useEffect, useContext, etc.)
- JSX elements and components
- Props and PropTypes
- Default props and defaultProps
- React.memo, React.forwardRef, React.lazy
- Context providers and consumers
- Higher-order components (HOCs)
"""
import re
from pathlib import Path
from typing import Dict, List, Set
from .javascript_parser import JavaScriptParser


class ReactParser(JavaScriptParser):
    """Enhanced React/JSX parser with React-specific feature detection."""
    
    # React-specific patterns
    FUNCTION_COMPONENT_RE = re.compile(
        r'(?:export\s+(?:default\s+)?)?(?:const|let|var|function)\s+([A-Z]\w*)\s*[=:]\s*(?:\([^)]*\)|[^=]*)\s*(?:=>)?\s*(?:\{|return)'
    )
    CLASS_COMPONENT_RE = re.compile(
        r'class\s+([A-Z]\w*)\s+extends\s+(?:React\.)?(?:Component|PureComponent)'
    )
    HOOK_RE = re.compile(r'\b(use[A-Z]\w*)\s*\(')
    JSX_ELEMENT_RE = re.compile(r'<([A-Z][A-Za-z0-9]*)[^>]*(?:/>|>)')
    PROPS_RE = re.compile(r'(?:props|{\s*([^}]+)\s*})\s*[=:]')
    PROP_TYPES_RE = re.compile(r'(\w+)\.propTypes\s*=\s*\{')
    DEFAULT_PROPS_RE = re.compile(r'(\w+)\.defaultProps\s*=\s*\{')
    MEMO_RE = re.compile(r'React\.memo\s*\(\s*([A-Z]\w*)')
    FORWARD_REF_RE = re.compile(r'React\.forwardRef\s*\(')
    LAZY_RE = re.compile(r'React\.lazy\s*\(\s*\(\s*\)\s*=>\s*import\s*\([\'"]([^\'"]+)[\'"]')
    CONTEXT_RE = re.compile(r'(?:const|let|var)\s+(\w+Context)\s*=\s*React\.createContext')
    HOC_RE = re.compile(r'(?:export\s+(?:default\s+)?)?(?:const|function)\s+(with[A-Z]\w*)\s*\(')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse React/JSX file and extract all React-specific constructs."""
        # Start with JavaScript parsing
        data = super().parse_file(path)
        
        # Read file content
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return data
        
        lines = text.splitlines()
        
        # Extract React-specific features
        function_components = self._extract_function_components(text, lines, path)
        class_components = self._extract_class_components(text, lines, path)
        hooks = self._extract_hooks(text, lines)
        jsx_elements = self._extract_jsx_elements(text)
        props = self._extract_props(text, lines)
        prop_types = self._extract_prop_types(text, lines, path)
        default_props = self._extract_default_props(text, lines, path)
        memo_components = self._extract_memo_components(text)
        forward_refs = self._extract_forward_refs(text, lines)
        lazy_components = self._extract_lazy_components(text)
        contexts = self._extract_contexts(text, lines, path)
        hocs = self._extract_hocs(text, lines, path)
        
        # Add React features to result
        data['function_components'] = function_components
        data['class_components'] = class_components
        data['hooks'] = hooks
        data['jsx_elements'] = jsx_elements
        data['props'] = props
        data['prop_types'] = prop_types
        data['default_props'] = default_props
        data['memo_components'] = memo_components
        data['forward_refs'] = forward_refs
        data['lazy_components'] = lazy_components
        data['contexts'] = contexts
        data['hocs'] = hocs
        
        # Update language tag
        for meta in data.get("files", {}).values():
            meta["language"] = "react"
            meta["react_features"] = {
                "function_components": len(function_components),
                "class_components": len(class_components),
                "hooks_used": len(set([h['name'] for h in hooks])),
                "jsx_elements": len(set(jsx_elements)),
                "contexts": len(contexts),
                "hocs": len(hocs),
            }
        
        return data
    
    def _extract_function_components(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract React function components."""
        components = {}
        
        # Look for functions that start with uppercase (React convention)
        for match in self.FUNCTION_COMPONENT_RE.finditer(text):
            name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Check if it returns JSX (has < followed by uppercase letter)
            func_start = match.start()
            # Find the function body (rough estimate)
            func_body = text[func_start:min(func_start + 2000, len(text))]
            has_jsx = bool(re.search(r'return\s*(?:\(|\n)?\s*<[A-Z]', func_body))
            
            if has_jsx or name.endswith('Component') or name.startswith('use') == False:
                components[f"{path}::{name}"] = {
                    "id": f"{path}::{name}",
                    "name": name,
                    "file": str(path),
                    "line": line_no,
                    "kind": "function_component",
                    "has_jsx": has_jsx,
                }
        
        return components
    
    def _extract_class_components(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract React class components."""
        components = {}
        
        for match in self.CLASS_COMPONENT_RE.finditer(text):
            name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Find lifecycle methods in this component
            class_start = match.start()
            # Rough estimate of class body
            class_body = text[class_start:min(class_start + 5000, len(text))]
            
            lifecycle_methods = []
            for method in ['componentDidMount', 'componentDidUpdate', 'componentWillUnmount', 
                          'shouldComponentUpdate', 'render', 'constructor']:
                if method in class_body:
                    lifecycle_methods.append(method)
            
            components[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line": line_no,
                "kind": "class_component",
                "lifecycle_methods": lifecycle_methods,
            }
        
        return components
    
    def _extract_hooks(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract React Hooks usage."""
        hooks = []
        seen = set()
        
        for match in self.HOOK_RE.finditer(text):
            hook_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{hook_name}:{line_no}"
            if key not in seen:
                seen.add(key)
                hooks.append({
                    "name": hook_name,
                    "line": line_no,
                })
        
        return hooks
    
    def _extract_jsx_elements(self, text: str) -> List[str]:
        """Extract JSX elements/components used."""
        elements = set()
        
        for match in self.JSX_ELEMENT_RE.finditer(text):
            element_name = match.group(1)
            # Only React components (start with uppercase)
            if element_name[0].isupper():
                elements.add(element_name)
        
        return sorted(list(elements))
    
    def _extract_props(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract props definitions from function parameters."""
        props = []
        
        # Look for destructured props in function parameters
        destructure_re = re.compile(r'(?:function|const)\s+\w+\s*\(\s*\{\s*([^}]+)\s*\}')
        for match in destructure_re.finditer(text):
            prop_names = [p.strip().split(':')[0].strip() for p in match.group(1).split(',')]
            line_no = text[:match.start()].count('\n') + 1
            
            props.append({
                "line": line_no,
                "props": prop_names,
                "destructured": True,
            })
        
        return props
    
    def _extract_prop_types(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract PropTypes definitions."""
        prop_types = {}
        
        for match in self.PROP_TYPES_RE.finditer(text):
            component_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            prop_types[f"{path}::{component_name}"] = {
                "component": component_name,
                "line": line_no,
            }
        
        return prop_types
    
    def _extract_default_props(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract defaultProps definitions."""
        default_props = {}
        
        for match in self.DEFAULT_PROPS_RE.finditer(text):
            component_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            default_props[f"{path}::{component_name}"] = {
                "component": component_name,
                "line": line_no,
            }
        
        return default_props
    
    def _extract_memo_components(self, text: str) -> List[Dict]:
        """Extract React.memo wrapped components."""
        memo_components = []
        
        for match in self.MEMO_RE.finditer(text):
            component_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            memo_components.append({
                "component": component_name,
                "line": line_no,
            })
        
        return memo_components
    
    def _extract_forward_refs(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract React.forwardRef usage."""
        forward_refs = []
        
        for match in self.FORWARD_REF_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            forward_refs.append({"line": line_no})
        
        return forward_refs
    
    def _extract_lazy_components(self, text: str) -> List[Dict]:
        """Extract React.lazy components."""
        lazy_components = []
        
        for match in self.LAZY_RE.finditer(text):
            import_path = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            lazy_components.append({
                "import_path": import_path,
                "line": line_no,
            })
        
        return lazy_components
    
    def _extract_contexts(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract React Context definitions."""
        contexts = {}
        
        for match in self.CONTEXT_RE.finditer(text):
            context_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            contexts[f"{path}::{context_name}"] = {
                "id": f"{path}::{context_name}",
                "name": context_name,
                "file": str(path),
                "line": line_no,
                "kind": "context",
            }
        
        return contexts
    
    def _extract_hocs(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Higher-Order Components (HOCs)."""
        hocs = {}
        
        for match in self.HOC_RE.finditer(text):
            hoc_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            hocs[f"{path}::{hoc_name}"] = {
                "id": f"{path}::{hoc_name}",
                "name": hoc_name,
                "file": str(path),
                "line": line_no,
                "kind": "hoc",
            }
        
        return hocs
