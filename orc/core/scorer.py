"""
ORC Core: Code Health Scoring
"""
from typing import Dict
from .indexer import ModuleInfo

class Scorer:
    """Calculate health scores and complexity metrics"""

    def __init__(self, config):
        self.config = config

    def calculate_health_score(self, modules: Dict[str, ModuleInfo]) -> float:
        """Calculate overall code health score (0-100)"""
        if not modules:
            return 100.0

        scores = []

        # Calculate individual metrics
        complexity_score = self._calculate_complexity_score(modules)
        coupling_score = self._calculate_coupling_score(modules)
        dead_code_score = self._calculate_dead_code_score(modules)
        duplication_score = self._calculate_duplication_score(modules)

        # Weighted average of all scores
        scores.append(('complexity', complexity_score, 0.3))
        scores.append(('coupling', coupling_score, 0.25))
        scores.append(('dead_code', dead_code_score, 0.25))
        scores.append(('duplication', duplication_score, 0.2))

        # Calculate weighted average
        total_weighted_score = sum(score * weight for _, score, weight in scores)
        total_weight = sum(weight for _, _, weight in scores)

        return total_weighted_score if total_weight > 0 else 100.0

    def _calculate_complexity_score(self, modules: Dict[str, ModuleInfo]) -> float:
        """Calculate score based on cyclomatic complexity"""
        if not modules:
            return 100.0

        total_functions = 0
        high_complexity_functions = 0

        for module in modules.values():
            for func in module.functions.values():
                total_functions += 1
                if func.complexity > self.config.min_complexity_threshold:
                    high_complexity_functions += 1

        if total_functions == 0:
            return 100.0

        ratio = high_complexity_functions / total_functions
        # Lower ratio is better, so invert it for scoring
        return max(0, 100 * (1 - ratio))

    def _calculate_coupling_score(self, modules: Dict[str, ModuleInfo]) -> float:
        """Calculate score based on module coupling"""
        # This would require dependency graph to calculate properly
        # For now, we'll use a simple heuristic based on import count
        if not modules:
            return 100.0

        total_modules = len(modules)
        total_imports = sum(len(module.imports) for module in modules.values())

        if total_modules == 0:
            return 100.0

        avg_imports_per_module = total_imports / total_modules
        # Higher coupling is worse, so invert
        # Assuming 10 imports per module is the threshold for "bad" coupling
        coupling_ratio = min(avg_imports_per_module / 10.0, 1.0)
        return max(0, 100 * (1 - coupling_ratio))

    def _calculate_dead_code_score(self, modules: Dict[str, ModuleInfo]) -> float:
        """Calculate score based on dead code detection"""
        # This would require dead code analysis results
        # For now, we'll return a placeholder score
        return 100.0  # Placeholder - actual implementation would analyze dead code

    def _calculate_duplication_score(self, modules: Dict[str, ModuleInfo]) -> float:
        """Calculate score based on code duplication"""
        # This would require duplication analysis
        # For now, we'll return a placeholder score
        return 100.0  # Placeholder - actual implementation would analyze duplication

    def get_detailed_scores(self, modules: Dict[str, ModuleInfo]) -> Dict[str, float]:
        """Get detailed breakdown of all scores"""
        return {
            'complexity_score': self._calculate_complexity_score(modules),
            'coupling_score': self._calculate_coupling_score(modules),
            'dead_code_score': self._calculate_dead_code_score(modules),
            'duplication_score': self._calculate_duplication_score(modules),
            'overall_score': self.calculate_health_score(modules)
        }
