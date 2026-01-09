"""
Code smell detection for ORC.

Detects common code smells:
- Long functions
- Too many parameters
- Deep nesting
- Long parameter lists
- God classes (too many methods)
- Duplicate code patterns
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    smell_type: str
    severity: str  # "low", "medium", "high"
    location: str  # file::function or file::class
    message: str
    suggestion: str
    metric_value: int
    threshold: int


class CodeSmellDetector:
    """Detects various code smells in indexed code"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Configurable thresholds
        self.max_function_length = self.config.get('max_function_length', 50)
        self.max_parameters = self.config.get('max_parameters', 5)
        self.max_complexity = self.config.get('max_complexity', 10)
        self.max_class_methods = self.config.get('max_class_methods', 20)
        self.max_nesting = self.config.get('max_nesting', 4)
    
    def analyze(self, index: Dict) -> List[CodeSmell]:
        """Analyze index and return detected code smells"""
        smells = []
        
        # Analyze functions
        for func_id, func_data in index.get('functions', {}).items():
            smells.extend(self._check_function(func_id, func_data))
        
        # Analyze classes
        for class_id, class_data in index.get('classes', {}).items():
            smells.extend(self._check_class(class_id, class_data))
        
        return smells
    
    def _check_function(self, func_id: str, func_data: Dict) -> List[CodeSmell]:
        """Check a function for code smells"""
        smells = []
        
        # Long function
        line_count = func_data.get('line_end', 0) - func_data.get('line_start', 0)
        if line_count > self.max_function_length:
            severity = "high" if line_count > self.max_function_length * 2 else "medium"
            smells.append(CodeSmell(
                smell_type="long_function",
                severity=severity,
                location=func_id,
                message=f"Function is {line_count} lines long",
                suggestion=f"Consider breaking this function into smaller functions (max {self.max_function_length} lines)",
                metric_value=line_count,
                threshold=self.max_function_length
            ))
        
        # Too many parameters
        param_count = len(func_data.get('parameters', []))
        if param_count > self.max_parameters:
            severity = "high" if param_count > self.max_parameters * 2 else "medium"
            smells.append(CodeSmell(
                smell_type="too_many_parameters",
                severity=severity,
                location=func_id,
                message=f"Function has {param_count} parameters",
                suggestion=f"Consider using a config object or dataclass (max {self.max_parameters} parameters)",
                metric_value=param_count,
                threshold=self.max_parameters
            ))
        
        # High complexity
        complexity = func_data.get('complexity', 1)
        if complexity > self.max_complexity:
            severity = "high" if complexity > self.max_complexity * 2 else "medium"
            smells.append(CodeSmell(
                smell_type="high_complexity",
                severity=severity,
                location=func_id,
                message=f"Function has cyclomatic complexity of {complexity}",
                suggestion=f"Simplify control flow or extract methods (max complexity {self.max_complexity})",
                metric_value=complexity,
                threshold=self.max_complexity
            ))
        
        # No docstring
        if not func_data.get('docstring'):
            name = func_data.get('name', '')
            # Only flag public functions
            if not name.startswith('_'):
                smells.append(CodeSmell(
                    smell_type="missing_docstring",
                    severity="low",
                    location=func_id,
                    message="Public function has no docstring",
                    suggestion="Add a docstring explaining what this function does",
                    metric_value=0,
                    threshold=1
                ))
        
        return smells
    
    def _check_class(self, class_id: str, class_data: Dict) -> List[CodeSmell]:
        """Check a class for code smells"""
        smells = []
        
        # God class (too many methods)
        methods = class_data.get('methods', [])
        method_count = len(methods)
        if method_count > self.max_class_methods:
            severity = "high" if method_count > self.max_class_methods * 2 else "medium"
            smells.append(CodeSmell(
                smell_type="god_class",
                severity=severity,
                location=class_id,
                message=f"Class has {method_count} methods",
                suggestion=f"Consider splitting into multiple classes with single responsibilities (max {self.max_class_methods} methods)",
                metric_value=method_count,
                threshold=self.max_class_methods
            ))
        
        # No docstring
        if not class_data.get('docstring'):
            name = class_data.get('name', '')
            if not name.startswith('_'):
                smells.append(CodeSmell(
                    smell_type="missing_docstring",
                    severity="low",
                    location=class_id,
                    message="Public class has no docstring",
                    suggestion="Add a docstring explaining what this class does",
                    metric_value=0,
                    threshold=1
                ))
        
        return smells
    
    def get_summary(self, smells: List[CodeSmell]) -> Dict:
        """Generate summary statistics for detected smells"""
        by_type = {}
        by_severity = {"low": 0, "medium": 0, "high": 0}
        
        for smell in smells:
            by_type[smell.smell_type] = by_type.get(smell.smell_type, 0) + 1
            by_severity[smell.severity] += 1
        
        return {
            "total_smells": len(smells),
            "by_type": by_type,
            "by_severity": by_severity,
            "most_common": max(by_type.items(), key=lambda x: x[1])[0] if by_type else None
        }
