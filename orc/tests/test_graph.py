"""
ORC Tests: Graph Builder Module Tests
"""
import pytest
from unittest.mock import Mock
from pathlib import Path

from orc.core.graph_builder import DependencyGraph
from orc.core.indexer import ModuleInfo, FunctionInfo

class TestDependencyGraph:
    def setup_method(self):
        """Set up test fixtures"""
        self.graph = DependencyGraph()

    def test_initialization(self):
        """Test graph initialization"""
        assert self.graph.module_graph is not None
        assert self.graph.call_graph is not None
        assert self.graph.function_map is not None

    def test_build_from_empty_modules(self):
        """Test building graph from empty modules"""
        modules = {}
        self.graph.build_from_modules(modules)
        
        # Graphs should be empty
        assert len(self.graph.module_graph.nodes()) == 0
        assert len(self.graph.call_graph.nodes()) == 0

    def test_build_from_single_module(self):
        """Test building graph from single module"""
        modules = {
            'module1.py': ModuleInfo(
                path='module1.py',
                lines=50,
                imports=[],
                exports=['func1'],
                functions={
                    'func1': FunctionInfo(
                        name='func1',
                        file_path='module1.py',
                        line_start=5,
                        line_end=10,
                        complexity=3,
                        calls=[],
                        called_by=set(),
                        parameters=['x'],
                        is_exported=True,
                        is_used=True,
                        docstring='Sample function'
                    )
                },
                classes=['MyClass'],
                last_modified=0.0,
                hash='abc123'
            )
        }
        
        self.graph.build_from_modules(modules)
        
        # Check module graph
        assert 'module1.py' in self.graph.module_graph.nodes()
        node_data = self.graph.module_graph.nodes['module1.py']
        assert node_data['lines'] == 50
        assert node_data['functions'] == 1
        
        # Check call graph
        func_id = 'module1.py::func1'
        assert func_id in self.graph.call_graph.nodes()
        func_data = self.graph.call_graph.nodes[func_id]
        assert func_data['complexity'] == 3

    def test_build_with_function_calls(self):
        """Test building graph with function calls"""
        modules = {
            'module1.py': ModuleInfo(
                path='module1.py',
                lines=100,
                imports=[],
                exports=['func_a', 'func_b'],
                functions={
                    'func_a': FunctionInfo(
                        name='func_a',
                        file_path='module1.py',
                        line_start=5,
                        line_end=10,
                        complexity=2,
                        calls=['func_b'],  # func_a calls func_b
                        called_by=set(),
                        parameters=[],
                        is_exported=True,
                        is_used=True,
                        docstring=None
                    ),
                    'func_b': FunctionInfo(
                        name='func_b',
                        file_path='module1.py',
                        line_start=12,
                        line_end=17,
                        complexity=1,
                        calls=[],  # func_b calls nothing
                        called_by={'module1.py::func_a'},  # func_b is called by func_a
                        parameters=[],
                        is_exported=True,
                        is_used=True,
                        docstring=None
                    )
                },
                classes=[],
                last_modified=0.0,
                hash='hash1'
            )
        }
        
        self.graph.build_from_modules(modules)
        
        # Check that there's a call edge from func_a to func_b
        func_a_id = 'module1.py::func_a'
        func_b_id = 'module1.py::func_b'
        
        assert self.graph.call_graph.has_edge(func_a_id, func_b_id)
        
        # Check callers and callees
        callers_of_b = self.graph.get_function_callers(func_b_id)
        assert func_a_id in callers_of_b
        
        callees_of_a = self.graph.get_function_callees(func_a_id)
        assert func_b_id in callees_of_a

    def test_find_circular_dependencies_empty(self):
        """Test finding circular dependencies in empty graph"""
        cycles = self.graph.find_circular_dependencies()
        assert cycles == []

    def test_get_module_dependencies(self):
        """Test getting module dependencies"""
        modules = {
            'module1.py': ModuleInfo(
                path='module1.py',
                lines=50,
                imports=['module2'],
                exports=['func1'],
                functions={
                    'func1': FunctionInfo(
                        name='func1',
                        file_path='module1.py',
                        line_start=5,
                        line_end=10,
                        complexity=2,
                        calls=[],
                        called_by=set(),
                        parameters=[],
                        is_exported=True,
                        is_used=True,
                        docstring=None
                    )
                },
                classes=[],
                last_modified=0.0,
                hash='hash1'
            ),
            'module2.py': ModuleInfo(
                path='module2.py',
                lines=30,
                imports=[],
                exports=['func2'],
                functions={
                    'func2': FunctionInfo(
                        name='func2',
                        file_path='module2.py',
                        line_start=3,
                        line_end=8,
                        complexity=1,
                        calls=[],
                        called_by=set(),
                        parameters=[],
                        is_exported=True,
                        is_used=True,
                        docstring=None
                    )
                },
                classes=[],
                last_modified=0.0,
                hash='hash2'
            )
        }
        
        self.graph.build_from_modules(modules)
        
        # Get dependencies for module1
        deps = self.graph.get_module_dependencies('module1.py')
        # module1 depends on module2 (through import)
        assert 'module2.py' in deps['depends_on']
        # module2 is depended on by module1
        assert 'module1.py' in deps['depended_by']

    def test_calculate_module_coupling(self):
        """Test calculating module coupling"""
        modules = {
            'module1.py': ModuleInfo(
                path='module1.py',
                lines=50,
                imports=['module2', 'module3'],
                exports=['func1'],
                functions={'func1': FunctionInfo(
                    name='func1', file_path='module1.py', line_start=5, line_end=10,
                    complexity=2, calls=[], called_by=set(), parameters=[],
                    is_exported=True, is_used=True, docstring=None
                )},
                classes=[],
                last_modified=0.0,
                hash='hash1'
            ),
            'module2.py': ModuleInfo(
                path='module2.py',
                lines=30,
                imports=[],
                exports=['func2'],
                functions={'func2': FunctionInfo(
                    name='func2', file_path='module2.py', line_start=3, line_end=8,
                    complexity=1, calls=[], called_by=set(), parameters=[],
                    is_exported=True, is_used=True, docstring=None
                )},
                classes=[],
                last_modified=0.0,
                hash='hash2'
            ),
            'module3.py': ModuleInfo(
                path='module3.py',
                lines=25,
                imports=[],
                exports=['func3'],
                functions={'func3': FunctionInfo(
                    name='func3', file_path='module3.py', line_start=2, line_end=7,
                    complexity=1, calls=[], called_by=set(), parameters=[],
                    is_exported=True, is_used=True, docstring=None
                )},
                classes=[],
                last_modified=0.0,
                hash='hash3'
            )
        }
        
        self.graph.build_from_modules(modules)
        
        # module1 has 2 dependencies (module2, module3), and there are 3 total modules
        # coupling = (2 + 0) / (3 - 1) = 2/2 = 1.0 (where 0 is the number of modules depending on module1)
        coupling = self.graph.calculate_module_coupling('module1.py')
        # Since module1 depends on 2 modules and 0 modules depend on it, total deps = 2
        # With 3 total modules, coupling = 2 / (3-1) = 1.0
        assert coupling == 1.0