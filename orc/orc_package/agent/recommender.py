"""
ORC Agent: Recommendation Generator
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from orc.core.indexer import ModuleInfo
from orc.core.graph_builder import DependencyGraph

class Priority(Enum):
    """Recommendation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(Enum):
    """Recommendation categories"""
    DEAD_CODE = "dead_code"
    COMPLEXITY = "complexity"
    DEPENDENCIES = "dependencies"
    STRUCTURE = "structure"
    PERFORMANCE = "performance"

@dataclass
class Recommendation:
    """A single recommendation"""
    title: str
    description: str
    category: Category
    priority: Priority
    impact: str
    effort: str
    files: List[str]
    lines_affected: int
    suggested_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority.value,
            'impact': self.impact,
            'effort': self.effort,
            'files': self.files,
            'lines_affected': self.lines_affected,
            'suggested_action': self.suggested_action
        }

class Recommender:
    """Generate actionable recommendations for codebase improvements"""

    def __init__(self, config, modules: Dict[str, ModuleInfo], graph: DependencyGraph):
        self.config = config
        self.modules = modules
        self.graph = graph
        self.recommendations: List[Recommendation] = []

    def generate_recommendations(self) -> List[Recommendation]:
        """Generate all recommendations"""
        self.recommendations = []

        self._analyze_dead_code()
        self._analyze_complexity()
        self._analyze_dependencies()
        self._analyze_structure()

        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3
        }
        self.recommendations.sort(key=lambda r: priority_order[r.priority])

        return self.recommendations

    def _analyze_dead_code(self):
        """Generate dead code removal recommendations"""
        from orc.analysis.dead_code import DeadCodeAnalyzer
        analyzer = DeadCodeAnalyzer(self.config)
        report = analyzer.analyze(self.modules)

        if report.unused_functions:
            # Focus on functions that would save significant lines
            high_value_removals = [f for f in report.unused_functions if f.get('lines', 0) > 10]

            if high_value_removals:
                lines_saved = sum(f.get('lines', 0) for f in high_value_removals)
                self.recommendations.append(Recommendation(
                    title=f"Remove {len(high_value_removals)} unused functions",
                    description=f"Found {len(high_value_removals)} unused functions that can be safely removed",
                    category=Category.DEAD_CODE,
                    priority=Priority.HIGH,
                    impact=f"Remove {lines_saved} lines of unused code",
                    effort="low",
                    files=list(set(f['file'] for f in high_value_removals)),
                    lines_affected=lines_saved,
                    suggested_action="Review and delete these functions after confirming they're not used dynamically"
                ))

        if report.unused_files:
            total_lines = 0
            for file_path in report.unused_files:
                if file_path in self.modules:
                    total_lines += self.modules[file_path].lines
            
            self.recommendations.append(Recommendation(
                title=f"Remove {len(report.unused_files)} unused files",
                description="These files are never imported by other modules",
                category=Category.DEAD_CODE,
                priority=Priority.MEDIUM,
                impact=f"Remove {total_lines} lines of unused code",
                effort="low",
                files=report.unused_files,
                lines_affected=total_lines,
                suggested_action="Archive or delete these files after verification"
            ))

    def _analyze_complexity(self):
        """Generate complexity reduction recommendations"""
        complex_functions = []

        for path, module in self.modules.items():
            for func_name, func_info in module.functions.items():
                if func_info.complexity > self.config.min_complexity_threshold:
                    complex_functions.append({
                        'name': func_name,
                        'file': path,
                        'complexity': func_info.complexity,
                        'line_start': func_info.line_start,
                        'line_end': func_info.line_end,
                        'lines': func_info.line_end - func_info.line_start + 1
                    })

        if complex_functions:
            # Critical: Very high complexity functions
            critical = [f for f in complex_functions if f['complexity'] > 20]
            if critical:
                self.recommendations.append(Recommendation(
                    title=f"Refactor {len(critical)} highly complex functions",
                    description="Functions with complexity > 20 are very difficult to maintain",
                    category=Category.COMPLEXITY,
                    priority=Priority.CRITICAL,
                    impact="Significantly improve maintainability and reduce bug risk",
                    effort="high",
                    files=list(set(f['file'] for f in critical)),
                    lines_affected=sum(f['lines'] for f in critical),
                    suggested_action="Break down into smaller functions, extract helper methods, reduce branching"
                ))

            # High: Moderately high complexity functions
            high = [f for f in complex_functions if self.config.min_complexity_threshold < f['complexity'] <= 20]
            if high:
                self.recommendations.append(Recommendation(
                    title=f"Simplify {len(high)} complex functions",
                    description="Functions with high complexity should be simplified",
                    category=Category.COMPLEXITY,
                    priority=Priority.HIGH,
                    impact="Improve readability and testability",
                    effort="medium",
                    files=list(set(f['file'] for f in high)),
                    lines_affected=sum(f['lines'] for f in high),
                    suggested_action="Reduce branching logic, extract conditions into separate functions"
                ))

    def _analyze_dependencies(self):
        """Generate dependency-related recommendations"""
        # Find circular dependencies
        cycles = self.graph.find_circular_dependencies()
        if cycles:
            self.recommendations.append(Recommendation(
                title=f"Break {len(cycles)} circular dependency cycles",
                description="Circular dependencies make code harder to test and understand",
                category=Category.DEPENDENCIES,
                priority=Priority.HIGH,
                impact="Improve code modularity and testability",
                effort="high",
                files=[f for cycle in cycles for f in cycle],
                lines_affected=0,  # Doesn't directly affect lines
                suggested_action="Introduce interfaces/abstractions or restructure modules"
            ))

        # Find highly coupled modules
        coupling_issues = []
        for path in self.modules.keys():
            coupling_score = self.graph.calculate_module_coupling(path)
            if coupling_score > 0.5:  # Threshold for high coupling
                deps = self.graph.get_module_dependencies(path)
                coupling_issues.append({
                    'module': path,
                    'coupling_score': coupling_score,
                    'depends_on_count': len(deps['depends_on']),
                    'depended_by_count': len(deps['depended_by'])
                })

        if coupling_issues:
            self.recommendations.append(Recommendation(
                title=f"Reduce coupling in {len(coupling_issues)} modules",
                description="Highly coupled modules are difficult to change independently",
                category=Category.DEPENDENCIES,
                priority=Priority.MEDIUM,
                impact="Improve modularity and enable easier refactoring",
                effort="high",
                files=[issue['module'] for issue in coupling_issues],
                lines_affected=0,
                suggested_action="Apply dependency inversion, use interfaces, reduce shared state"
            ))

    def _analyze_structure(self):
        """Generate structural recommendations"""
        # Find large files
        large_files = []
        for path, module in self.modules.items():
            if module.lines > 1000 or len(module.functions) > 30:  # Arbitrary thresholds
                large_files.append({
                    'file': path,
                    'lines': module.lines,
                    'functions': len(module.functions)
                })

        if large_files:
            total_lines = sum(f['lines'] for f in large_files)
            self.recommendations.append(Recommendation(
                title=f"Split {len(large_files)} oversized files",
                description="Large files are difficult to navigate and understand",
                category=Category.STRUCTURE,
                priority=Priority.MEDIUM,
                impact=f"Improve organization by splitting {total_lines} lines of code",
                effort="medium",
                files=[f['file'] for f in large_files],
                lines_affected=total_lines,
                suggested_action="Split into multiple files by functional area or domain"
            ))

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of recommendations"""
        if not self.recommendations:
            self.generate_recommendations()

        by_priority = {p: 0 for p in Priority}
        by_category = {c: 0 for c in Category}
        total_lines = 0

        for rec in self.recommendations:
            by_priority[rec.priority] += 1
            by_category[rec.category] += 1
            total_lines += rec.lines_affected

        return {
            'total_recommendations': len(self.recommendations),
            'by_priority': {p.value: count for p, count in by_priority.items()},
            'by_category': {c.value: count for c, count in by_category.items()},
            'total_lines_affected': total_lines
        }

    def get_quick_wins(self) -> List[Recommendation]:
        """Get recommendations that are high impact, low effort"""
        return [
            r for r in self.recommendations
            if r.effort == "low" and r.priority in [Priority.CRITICAL, Priority.HIGH]
        ]