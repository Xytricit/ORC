"""TypeScript parser with full support for TypeScript-specific features.

Extracts:
- Interfaces, types, enums
- Generics and type parameters
- Decorators
- Classes with access modifiers (public, private, protected)
- Functions with type annotations
- Imports/exports (including type imports)
- Namespaces and modules
"""
import re
from pathlib import Path
from typing import Dict, List, Set
from .javascript_parser import JavaScriptParser


class TypeScriptParser(JavaScriptParser):
    """Enhanced TypeScript parser with TS-specific feature detection."""
    
    # TypeScript-specific patterns
    INTERFACE_RE = re.compile(r'(?:export\s+)?interface\s+(\w+)(?:<[^>]+>)?\s*(?:extends\s+[\w,\s<>]+)?\s*\{')
    TYPE_ALIAS_RE = re.compile(r'(?:export\s+)?type\s+(\w+)(?:<[^>]+>)?\s*=')
    ENUM_RE = re.compile(r'(?:export\s+)?enum\s+(\w+)\s*\{')
    DECORATOR_RE = re.compile(r'@(\w+)(?:\([^)]*\))?')
    TYPE_IMPORT_RE = re.compile(r'import\s+type\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]')
    NAMESPACE_RE = re.compile(r'(?:export\s+)?namespace\s+(\w+)\s*\{')
    GENERIC_RE = re.compile(r'<([^>]+)>')
    ACCESS_MODIFIER_RE = re.compile(r'\b(public|private|protected|readonly)\s+')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse TypeScript file and extract all TypeScript-specific constructs."""
        # Start with JavaScript parsing
        data = super().parse_file(path)
        
        # Read file content
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return data
        
        lines = text.splitlines()
        
        # Extract TypeScript-specific features
        interfaces = self._extract_interfaces(text, lines, path)
        type_aliases = self._extract_type_aliases(text, lines, path)
        enums = self._extract_enums(text, lines, path)
        decorators = self._extract_decorators(text, lines)
        type_imports = self._extract_type_imports(text)
        namespaces = self._extract_namespaces(text, lines, path)
        generics = self._extract_generics(text)
        
        # Add TypeScript features to result
        data['interfaces'] = interfaces
        data['type_aliases'] = type_aliases
        data['enums'] = enums
        data['decorators'] = decorators
        data['type_imports'] = type_imports
        data['namespaces'] = namespaces
        data['generics'] = generics
        
        # Update language tag
        for meta in data.get("files", {}).values():
            meta["language"] = "typescript"
            meta["typescript_features"] = {
                "interfaces": len(interfaces),
                "type_aliases": len(type_aliases),
                "enums": len(enums),
                "decorators": len(decorators),
                "type_imports": len(type_imports),
                "namespaces": len(namespaces),
            }
        
        return data
    
    def _extract_interfaces(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract TypeScript interfaces."""
        interfaces = {}
        for match in self.INTERFACE_RE.finditer(text):
            name = match.group(1)
            start_pos = match.start()
            line_no = text[:start_pos].count('\n') + 1
            
            # Find the closing brace
            brace_count = 1
            pos = match.end()
            while pos < len(text) and brace_count > 0:
                if text[pos] == '{':
                    brace_count += 1
                elif text[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            end_line = text[:pos].count('\n') + 1
            
            # Extract interface body
            body = text[match.end():pos-1]
            properties = self._extract_interface_properties(body)
            
            interfaces[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line_start": line_no,
                "line_end": end_line,
                "kind": "interface",
                "properties": properties,
            }
        
        return interfaces
    
    def _extract_interface_properties(self, body: str) -> List[Dict]:
        """Extract properties from interface body."""
        properties = []
        prop_re = re.compile(r'(\w+)(\?)?:\s*([^;,\n]+)')
        for match in prop_re.finditer(body):
            properties.append({
                "name": match.group(1),
                "optional": match.group(2) == '?',
                "type": match.group(3).strip(),
            })
        return properties
    
    def _extract_type_aliases(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract TypeScript type aliases."""
        type_aliases = {}
        for match in self.TYPE_ALIAS_RE.finditer(text):
            name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Find end of type (semicolon or newline)
            end_pos = text.find(';', match.end())
            if end_pos == -1:
                end_pos = text.find('\n', match.end())
            if end_pos == -1:
                end_pos = len(text)
            
            type_def = text[match.end():end_pos].strip()
            
            type_aliases[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line": line_no,
                "kind": "type_alias",
                "definition": type_def,
            }
        
        return type_aliases
    
    def _extract_enums(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract TypeScript enums."""
        enums = {}
        for match in self.ENUM_RE.finditer(text):
            name = match.group(1)
            start_pos = match.start()
            line_no = text[:start_pos].count('\n') + 1
            
            # Find closing brace
            brace_count = 1
            pos = match.end()
            while pos < len(text) and brace_count > 0:
                if text[pos] == '{':
                    brace_count += 1
                elif text[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            # Extract enum values
            body = text[match.end():pos-1]
            values = [v.strip().split('=')[0].strip() for v in body.split(',') if v.strip()]
            
            enums[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line": line_no,
                "kind": "enum",
                "values": values,
            }
        
        return enums
    
    def _extract_decorators(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract decorators (e.g., @Component, @Injectable)."""
        decorators = []
        seen = set()
        
        for match in self.DECORATOR_RE.finditer(text):
            decorator_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{decorator_name}:{line_no}"
            if key not in seen:
                seen.add(key)
                decorators.append({
                    "name": decorator_name,
                    "line": line_no,
                    "full_match": match.group(0),
                })
        
        return decorators
    
    def _extract_type_imports(self, text: str) -> List[Dict]:
        """Extract type-only imports."""
        type_imports = []
        for match in self.TYPE_IMPORT_RE.finditer(text):
            types = [t.strip() for t in match.group(1).split(',')]
            source = match.group(2)
            type_imports.append({
                "types": types,
                "from": source,
            })
        return type_imports
    
    def _extract_namespaces(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract TypeScript namespaces."""
        namespaces = {}
        for match in self.NAMESPACE_RE.finditer(text):
            name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            namespaces[f"{path}::{name}"] = {
                "id": f"{path}::{name}",
                "name": name,
                "file": str(path),
                "line": line_no,
                "kind": "namespace",
            }
        
        return namespaces
    
    def _extract_generics(self, text: str) -> List[str]:
        """Extract generic type parameters used in the file."""
        generics = set()
        for match in self.GENERIC_RE.finditer(text):
            params = match.group(1).split(',')
            for param in params:
                # Extract just the type parameter name (before any constraints)
                param_name = param.strip().split()[0].split('extends')[0].strip()
                if param_name and param_name[0].isupper():
                    generics.add(param_name)
        
        return sorted(list(generics))
