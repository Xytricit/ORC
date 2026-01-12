"""Django-specific parser built on top of PythonParser.

Extracts Django-specific patterns:
- Models (fields, relationships, Meta classes)
- Views (function-based and class-based views)
- URL patterns (urlpatterns, path, re_path)
- Forms (ModelForm, Form fields)
- Admin configurations
- Serializers (Django REST Framework)
- Managers and QuerySets
- Signals
- Template tags
"""
import re
from pathlib import Path
from typing import Dict, List
from .python_parser import PythonParser


class DjangoParser(PythonParser):
    """Enhanced Django parser with Django-specific pattern detection."""
    
    # Django-specific patterns
    MODEL_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:models\.Model|Model)')
    MODEL_FIELD_RE = re.compile(r'(\w+)\s*=\s*models\.(\w+Field)\s*\(')
    VIEW_CLASS_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:[\w.]*View|APIView|GenericAPIView)')
    URL_PATTERN_RE = re.compile(r'(?:path|re_path|url)\s*\(\s*[\'"]([^\'"]+)[\'"]')
    FORM_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:forms\.(?:Model)?Form|Form)')
    ADMIN_RE = re.compile(r'admin\.site\.register\s*\(\s*(\w+)')
    SERIALIZER_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:serializers\.\w+|ModelSerializer)')
    MANAGER_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:models\.Manager|Manager)')
    SIGNAL_RE = re.compile(r'@receiver\s*\(\s*(\w+)')
    TEMPLATE_TAG_RE = re.compile(r'@register\.(?:simple_tag|filter|inclusion_tag)')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse Django file and extract Django-specific constructs."""
        # Start with Python parsing
        data = super().parse_file(path)
        
        # Read file content
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return data
        
        lines = text.splitlines()
        
        # Extract Django-specific features
        models = self._extract_models(text, lines, path)
        views = self._extract_views(text, lines, path)
        url_patterns = self._extract_url_patterns(text)
        forms = self._extract_forms(text, lines, path)
        admin_registrations = self._extract_admin(text)
        serializers = self._extract_serializers(text, lines, path)
        managers = self._extract_managers(text, lines, path)
        signals = self._extract_signals(text, lines)
        template_tags = self._extract_template_tags(text, lines)
        
        # Add Django features to result
        data['django_models'] = models
        data['django_views'] = views
        data['django_urls'] = url_patterns
        data['django_forms'] = forms
        data['django_admin'] = admin_registrations
        data['django_serializers'] = serializers
        data['django_managers'] = managers
        data['django_signals'] = signals
        data['django_template_tags'] = template_tags
        
        # Update metadata
        for meta in data.get("files", {}).values():
            meta["framework"] = "django"
            meta["django_features"] = {
                "models": len(models),
                "views": len(views),
                "url_patterns": len(url_patterns),
                "forms": len(forms),
                "admin_registrations": len(admin_registrations),
                "serializers": len(serializers),
                "managers": len(managers),
                "signals": len(signals),
                "template_tags": len(template_tags),
            }
        
        return data
    
    def _extract_models(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Django models and their fields."""
        models = {}
        
        for match in self.MODEL_RE.finditer(text):
            model_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Find model fields within this class
            class_start = match.start()
            # Rough estimate of class end (next class or end of file)
            next_class = text.find('\nclass ', class_start + 1)
            class_end = next_class if next_class != -1 else len(text)
            class_body = text[class_start:class_end]
            
            fields = []
            for field_match in self.MODEL_FIELD_RE.finditer(class_body):
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                fields.append({
                    "name": field_name,
                    "type": field_type,
                })
            
            models[f"{path}::{model_name}"] = {
                "id": f"{path}::{model_name}",
                "name": model_name,
                "file": str(path),
                "line": line_no,
                "kind": "django_model",
                "fields": fields,
            }
        
        return models
    
    def _extract_views(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Django views (class-based and function-based)."""
        views = {}
        
        # Class-based views
        for match in self.VIEW_CLASS_RE.finditer(text):
            view_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            views[f"{path}::{view_name}"] = {
                "id": f"{path}::{view_name}",
                "name": view_name,
                "file": str(path),
                "line": line_no,
                "kind": "class_based_view",
            }
        
        # Function-based views (functions that take request as first param)
        # Already extracted by PythonParser, but we can mark them
        func_view_re = re.compile(r'def\s+(\w+)\s*\(\s*request\s*[,)]')
        for match in func_view_re.finditer(text):
            view_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            views[f"{path}::{view_name}"] = {
                "id": f"{path}::{view_name}",
                "name": view_name,
                "file": str(path),
                "line": line_no,
                "kind": "function_based_view",
            }
        
        return views
    
    def _extract_url_patterns(self, text: str) -> List[Dict]:
        """Extract URL patterns from urls.py files."""
        url_patterns = []
        
        for match in self.URL_PATTERN_RE.finditer(text):
            url_path = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            url_patterns.append({
                "path": url_path,
                "line": line_no,
            })
        
        return url_patterns
    
    def _extract_forms(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Django forms."""
        forms = {}
        
        for match in self.FORM_RE.finditer(text):
            form_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            forms[f"{path}::{form_name}"] = {
                "id": f"{path}::{form_name}",
                "name": form_name,
                "file": str(path),
                "line": line_no,
                "kind": "django_form",
            }
        
        return forms
    
    def _extract_admin(self, text: str) -> List[Dict]:
        """Extract admin.site.register calls."""
        admin_registrations = []
        
        for match in self.ADMIN_RE.finditer(text):
            model_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            admin_registrations.append({
                "model": model_name,
                "line": line_no,
            })
        
        return admin_registrations
    
    def _extract_serializers(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Django REST Framework serializers."""
        serializers = {}
        
        for match in self.SERIALIZER_RE.finditer(text):
            serializer_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            serializers[f"{path}::{serializer_name}"] = {
                "id": f"{path}::{serializer_name}",
                "name": serializer_name,
                "file": str(path),
                "line": line_no,
                "kind": "serializer",
            }
        
        return serializers
    
    def _extract_managers(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract custom model managers."""
        managers = {}
        
        for match in self.MANAGER_RE.finditer(text):
            manager_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            managers[f"{path}::{manager_name}"] = {
                "id": f"{path}::{manager_name}",
                "name": manager_name,
                "file": str(path),
                "line": line_no,
                "kind": "manager",
            }
        
        return managers
    
    def _extract_signals(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract Django signal receivers."""
        signals = []
        
        for match in self.SIGNAL_RE.finditer(text):
            signal_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            signals.append({
                "signal": signal_name,
                "line": line_no,
            })
        
        return signals
    
    def _extract_template_tags(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract custom template tags."""
        template_tags = []
        
        for match in self.TEMPLATE_TAG_RE.finditer(text):
            line_no = text[:match.start()].count('\n') + 1
            tag_type = match.group(0).split('.')[-1]
            
            template_tags.append({
                "type": tag_type,
                "line": line_no,
            })
        
        return template_tags
