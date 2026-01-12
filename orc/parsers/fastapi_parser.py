"""FastAPI parser built on top of PythonParser.

Extracts FastAPI-specific patterns:
- Route definitions (@app.get, @app.post, etc.)
- Path parameters and query parameters
- Pydantic models (BaseModel)
- Dependencies (Depends)
- Background tasks
- WebSocket routes
- Middleware
- APIRouter instances
- Response models
"""
import re
from pathlib import Path
from typing import Dict, List
from .python_parser import PythonParser


class FastAPIParser(PythonParser):
    """Enhanced FastAPI parser with FastAPI-specific pattern detection."""
    
    # FastAPI-specific patterns
    ROUTE_RE = re.compile(r'@(?:app|router)\.(?:get|post|put|delete|patch|options|head|trace|websocket)\s*\(\s*[\'"]([^\'"]+)[\'"]')
    PYDANTIC_MODEL_RE = re.compile(r'class\s+(\w+)\s*\(\s*(?:BaseModel|pydantic\.BaseModel)')
    DEPENDS_RE = re.compile(r'Depends\s*\(\s*(\w+)')
    BACKGROUND_TASK_RE = re.compile(r'BackgroundTasks')
    WEBSOCKET_RE = re.compile(r'@(?:app|router)\.websocket\s*\(\s*[\'"]([^\'"]+)[\'"]')
    MIDDLEWARE_RE = re.compile(r'@app\.middleware\s*\(\s*[\'"]([^\'"]+)[\'"]')
    API_ROUTER_RE = re.compile(r'(\w+)\s*=\s*APIRouter\s*\(')
    RESPONSE_MODEL_RE = re.compile(r'response_model\s*=\s*(\w+)')
    PATH_PARAM_RE = re.compile(r'\{(\w+)\}')
    QUERY_PARAM_RE = re.compile(r'(\w+):\s*(?:Optional\[)?(?:str|int|float|bool)')
    
    def parse_file(self, path: Path) -> Dict:
        """Parse FastAPI file and extract FastAPI-specific constructs."""
        # Start with Python parsing
        data = super().parse_file(path)
        
        # Read file content
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            return data
        
        lines = text.splitlines()
        
        # Extract FastAPI-specific features
        routes = self._extract_routes(text, lines)
        pydantic_models = self._extract_pydantic_models(text, lines, path)
        dependencies = self._extract_dependencies(text)
        websockets = self._extract_websockets(text, lines)
        middleware = self._extract_middleware(text, lines)
        api_routers = self._extract_api_routers(text, lines, path)
        response_models = self._extract_response_models(text)
        
        # Add FastAPI features to result
        data['fastapi_routes'] = routes
        data['fastapi_models'] = pydantic_models
        data['fastapi_dependencies'] = dependencies
        data['fastapi_websockets'] = websockets
        data['fastapi_middleware'] = middleware
        data['fastapi_routers'] = api_routers
        data['fastapi_response_models'] = response_models
        
        # Update metadata
        for meta in data.get("files", {}).values():
            meta["framework"] = "fastapi"
            meta["fastapi_features"] = {
                "routes": len(routes),
                "pydantic_models": len(pydantic_models),
                "dependencies": len(dependencies),
                "websockets": len(websockets),
                "middleware": len(middleware),
                "routers": len(api_routers),
            }
        
        return data
    
    def _extract_routes(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract FastAPI route definitions."""
        routes = []
        
        for match in self.ROUTE_RE.finditer(text):
            path = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Determine HTTP method
            method_match = re.search(r'@(?:app|router)\.(\w+)\s*\(', match.group(0))
            method = method_match.group(1).upper() if method_match else "UNKNOWN"
            
            # Extract path parameters
            path_params = self.PATH_PARAM_RE.findall(path)
            
            # Try to find the function name (next line usually)
            func_match = re.search(r'def\s+(\w+)\s*\(', text[match.end():match.end()+200])
            func_name = func_match.group(1) if func_match else None
            
            routes.append({
                "path": path,
                "method": method,
                "line": line_no,
                "function": func_name,
                "path_params": path_params,
            })
        
        return routes
    
    def _extract_pydantic_models(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract Pydantic BaseModel classes."""
        models = {}
        
        for match in self.PYDANTIC_MODEL_RE.finditer(text):
            model_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            # Find model fields within this class
            class_start = match.start()
            next_class = text.find('\nclass ', class_start + 1)
            class_end = next_class if next_class != -1 else len(text)
            class_body = text[class_start:class_end]
            
            # Extract field definitions
            fields = []
            field_re = re.compile(r'(\w+):\s*([^\n=]+)')
            for field_match in field_re.finditer(class_body):
                field_name = field_match.group(1)
                field_type = field_match.group(2).strip()
                # Skip class methods
                if field_name not in ['def', 'class', 'async']:
                    fields.append({
                        "name": field_name,
                        "type": field_type,
                    })
            
            models[f"{path}::{model_name}"] = {
                "id": f"{path}::{model_name}",
                "name": model_name,
                "file": str(path),
                "line": line_no,
                "kind": "pydantic_model",
                "fields": fields,
            }
        
        return models
    
    def _extract_dependencies(self, text: str) -> List[Dict]:
        """Extract Depends() usage for dependency injection."""
        dependencies = []
        seen = set()
        
        for match in self.DEPENDS_RE.finditer(text):
            dep_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{dep_name}:{line_no}"
            if key not in seen:
                seen.add(key)
                dependencies.append({
                    "dependency": dep_name,
                    "line": line_no,
                })
        
        return dependencies
    
    def _extract_websockets(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract WebSocket route definitions."""
        websockets = []
        
        for match in self.WEBSOCKET_RE.finditer(text):
            path = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            websockets.append({
                "path": path,
                "line": line_no,
            })
        
        return websockets
    
    def _extract_middleware(self, text: str, lines: List[str]) -> List[Dict]:
        """Extract middleware definitions."""
        middleware = []
        
        for match in self.MIDDLEWARE_RE.finditer(text):
            middleware_type = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            middleware.append({
                "type": middleware_type,
                "line": line_no,
            })
        
        return middleware
    
    def _extract_api_routers(self, text: str, lines: List[str], path: Path) -> Dict:
        """Extract APIRouter instances."""
        routers = {}
        
        for match in self.API_ROUTER_RE.finditer(text):
            router_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            routers[f"{path}::{router_name}"] = {
                "id": f"{path}::{router_name}",
                "name": router_name,
                "file": str(path),
                "line": line_no,
                "kind": "api_router",
            }
        
        return routers
    
    def _extract_response_models(self, text: str) -> List[Dict]:
        """Extract response_model declarations."""
        response_models = []
        seen = set()
        
        for match in self.RESPONSE_MODEL_RE.finditer(text):
            model_name = match.group(1)
            line_no = text[:match.start()].count('\n') + 1
            
            key = f"{model_name}:{line_no}"
            if key not in seen:
                seen.add(key)
                response_models.append({
                    "model": model_name,
                    "line": line_no,
                })
        
        return response_models
