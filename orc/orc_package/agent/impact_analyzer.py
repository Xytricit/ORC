"""
ORC Agent: Impact Analyzer
"""
from typing import Dict, List
from core.indexer import ModuleInfo
from core.graph_builder import DependencyGraph

class ImpactAnalyzer:
    """Assess the potential impact of code changes"""

    def __init__(self, config, modules: Dict[str, ModuleInfo], graph: DependencyGraph):
        self.config = config
        self.modules = modules
        self.graph = graph

    def assess_change_impact(self, change_description: Dict) -> Dict:
        """
        Assess the impact of a proposed change
        
        change_description should contain:
        - 'type': 'function_change', 'module_change', 'interface_change', etc.
        - 'target': the specific element being changed
        - 'scope': 'local', 'module', 'global'
        """
        change_type = change_description.get('type', 'unknown')
        target = change_description.get('target', '')
        
        if change_type == 'function_change':
            return self._assess_function_change(target)
        elif change_type == 'module_change':
            return self._assess_module_change(target)
        elif change_type == 'interface_change':
            return self._assess_interface_change(target)
        else:
            return self._assess_generic_change(target)

    def _assess_function_change(self, function_id: str) -> Dict:
        """Assess impact of changing a specific function"""
        # Parse function_id (format: "file_path::function_name")
        if '::' not in function_id:
            return {'error': 'Invalid function ID format'}
        
        file_path, func_name = function_id.split('::', 1)
        
        # Check if function exists
        if file_path not in self.modules:
            return {'error': f'Module {file_path} not found'}
        
        module = self.modules[file_path]
        if func_name not in module.functions:
            return {'error': f'Function {func_name} not found in {file_path}'}
        
        # Get function info
        func_info = module.functions[func_name]
        
        # Find all callers of this function
        callers = self.graph.get_function_callers(function_id)
        
        # Calculate impact metrics
        impact_score = len(callers)  # More callers = higher impact
        if func_info.complexity > self.config.min_complexity_threshold:
            impact_score *= 1.5  # Complex functions have higher impact when changed
        
        # Identify high-risk callers (functions in critical paths)
        high_risk_callers = []
        for caller_id in callers:
            if self._is_high_risk_function(caller_id):
                high_risk_callers.append(caller_id)
        
        return {
            'type': 'function_change',
            'target': function_id,
            'impact_score': min(impact_score, 10),  # Cap at 10
            'direct_callers': len(callers),
            'high_risk_callers': len(high_risk_callers),
            'estimated_test_effort': self._estimate_test_effort(len(callers)),
            'affected_modules': list(set(self._get_caller_modules(callers))),
            'risk_level': self._get_risk_level(impact_score),
            'recommendations': [
                f'Test {len(callers)} functions that call this function',
                'Review error handling if this function throws exceptions',
                'Check if return type changes affect callers'
            ]
        }

    def _assess_module_change(self, module_path: str) -> Dict:
        """Assess impact of changing a specific module"""
        if module_path not in self.modules:
            return {'error': f'Module {module_path} not found'}
        
        # Get module dependencies
        deps = self.graph.get_module_dependencies(module_path)
        
        # Calculate impact based on coupling
        coupling_score = self.graph.calculate_module_coupling(module_path)
        
        # Find all modules that depend on this module
        affected_by_change = deps['depended_by']
        
        # Find all modules this module depends on (change might affect how it works)
        depends_on = deps['depends_on']
        
        return {
            'type': 'module_change',
            'target': module_path,
            'impact_score': min(len(affected_by_change) * coupling_score * 2, 10),
            'modules_affected_by_change': len(affected_by_change),
            'modules_it_depends_on': len(depends_on),
            'coupling_score': coupling_score,
            'estimated_test_effort': self._estimate_test_effort(len(affected_by_change)),
            'risk_level': self._get_risk_level(len(affected_by_change) * coupling_score),
            'recommendations': [
                f'Test {len(affected_by_change)} modules that depend on this module',
                'Review public API if function signatures change',
                'Check integration points with dependent modules'
            ]
        }

    def _assess_interface_change(self, interface_name: str) -> Dict:
        """Assess impact of changing an interface (public API)"""
        # Find all functions that match the interface pattern
        matching_functions = []
        for path, module in self.modules.items():
            for func_name, func_info in module.functions.items():
                if interface_name.lower() in func_name.lower() or self._matches_interface_pattern(func_name, interface_name):
                    matching_functions.append(f"{path}::{func_name}")
        
        # Get all callers of these functions
        all_callers = set()
        for func_id in matching_functions:
            callers = self.graph.get_function_callers(func_id)
            all_callers.update(callers)
        
        return {
            'type': 'interface_change',
            'target': interface_name,
            'impact_score': min(len(all_callers) * 2, 10),  # Interfaces have high impact
            'affected_functions': len(matching_functions),
            'affected_callers': len(all_callers),
            'estimated_test_effort': self._estimate_test_effort(len(all_callers) * 2),
            'risk_level': 'high',
            'recommendations': [
                f'Test {len(all_callers)} functions affected by interface change',
                'Update all implementations if changing method signatures',
                'Check backward compatibility requirements'
            ]
        }

    def _assess_generic_change(self, target: str) -> Dict:
        """Assess impact of a generic change"""
        return {
            'type': 'generic_change',
            'target': target,
            'impact_score': 5,  # Default medium impact
            'estimated_test_effort': 'medium',
            'risk_level': 'medium',
            'recommendations': [
                'Perform regression testing',
                'Review related functionality'
            ]
        }

    def _is_high_risk_function(self, function_id: str) -> bool:
        """Determine if a function is high-risk to change"""
        if '::' not in function_id:
            return False
        
        file_path, func_name = function_id.split('::', 1)
        
        if file_path in self.modules:
            module = self.modules[file_path]
            if func_name in module.functions:
                func_info = module.functions[func_name]
                # High risk if complex or if function name suggests critical functionality
                return (func_info.complexity > self.config.min_complexity_threshold or
                        any(keyword in func_name.lower() for keyword in ['auth', 'security', 'payment', 'critical']))
        
        return False

    def _get_caller_modules(self, caller_ids: List[str]) -> List[str]:
        """Get unique modules from function caller IDs"""
        modules = set()
        for caller_id in caller_ids:
            if '::' in caller_id:
                module_path = caller_id.split('::')[0]
                modules.add(module_path)
        return list(modules)

    def _matches_interface_pattern(self, func_name: str, interface_name: str) -> bool:
        """Check if function name matches an interface pattern"""
        # Simple pattern matching - in a real system, this would be more sophisticated
        return interface_name.lower() in func_name.lower()

    def _estimate_test_effort(self, impact_factor: int) -> str:
        """Estimate testing effort based on impact"""
        if impact_factor == 0:
            return 'none'
        elif impact_factor <= 3:
            return 'low'
        elif impact_factor <= 10:
            return 'medium'
        else:
            return 'high'

    def _get_risk_level(self, impact_score: float) -> str:
        """Get risk level based on impact score"""
        if impact_score <= 2:
            return 'low'
        elif impact_score <= 5:
            return 'medium'
        elif impact_score <= 8:
            return 'high'
        else:
            return 'critical'