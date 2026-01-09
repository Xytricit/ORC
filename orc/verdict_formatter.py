"""
ORC Verdict Formatter - Delivers authoritative judgments on code quality.

ORC speaks with personality and conviction, not bland statistics.
"""

from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class VerdictLevel:
    """Verdict severity levels."""
    EXCELLENT = "EXCELLENT"
    SUSTAINABLE = "SUSTAINABLE"
    CONCERNING = "CONCERNING"
    UNSUSTAINABLE = "UNSUSTAINABLE"
    CRITICAL = "CRITICAL"


class OrcVerdict:
    """Formats ORC verdicts with personality and authority."""
    
    @staticmethod
    def determine_overall_verdict(metrics: Dict[str, Any]) -> str:
        """Determine overall verdict based on metrics."""
        # Calculate scores
        complexity_score = metrics.get('avg_complexity', 0)
        dead_code_pct = metrics.get('dead_code_percentage', 0)
        max_complexity = metrics.get('max_complexity', 0)
        critical_functions = metrics.get('critical_complexity_count', 0)
        
        # Verdict logic
        if max_complexity > 100 or dead_code_pct > 40 or critical_functions > 50:
            return VerdictLevel.CRITICAL
        elif max_complexity > 50 or dead_code_pct > 25 or critical_functions > 20:
            return VerdictLevel.UNSUSTAINABLE
        elif max_complexity > 30 or dead_code_pct > 15 or complexity_score > 8:
            return VerdictLevel.CONCERNING
        elif complexity_score < 5 and dead_code_pct < 5 and max_complexity < 20:
            return VerdictLevel.EXCELLENT
        else:
            return VerdictLevel.SUSTAINABLE
    
    @staticmethod
    def format_verdict(verdict: str, evidence: List[str], conclusion: str) -> None:
        """Display ORC verdict with dramatic formatting."""
        
        # Color mapping
        colors = {
            VerdictLevel.EXCELLENT: "bold green",
            VerdictLevel.SUSTAINABLE: "bold blue",
            VerdictLevel.CONCERNING: "bold yellow",
            VerdictLevel.UNSUSTAINABLE: "bold red",
            VerdictLevel.CRITICAL: "bold white on red"
        }
        
        color = colors.get(verdict, "bold white")
        
        # Build verdict text
        verdict_text = Text()
        verdict_text.append("\n")
        verdict_text.append("ORC VERDICT: ", style="bold cyan")
        verdict_text.append(verdict, style=color)
        verdict_text.append("\n\n")
        
        # Evidence
        if evidence:
            verdict_text.append("Evidence:\n", style="bold yellow")
            for item in evidence:
                verdict_text.append(f" • {item}\n", style="white")
            verdict_text.append("\n")
        
        # Conclusion
        verdict_text.append("Conclusion:\n", style="bold yellow")
        verdict_text.append(f"{conclusion}\n", style="italic white")
        
        # Display in panel
        panel = Panel(
            verdict_text,
            border_style=color,
            padding=(1, 2)
        )
        console.print(panel)
    
    @staticmethod
    def complexity_verdict(stats: Dict[str, Any]) -> None:
        """Generate verdict for complexity analysis."""
        avg = stats.get('average_complexity', 0)
        max_c = stats.get('max_complexity', 0)
        critical = stats.get('critical_count', 0)
        high = stats.get('high_count', 0)
        total = stats.get('total_functions', 0)
        
        evidence = []
        
        # Build evidence
        if critical > 0:
            pct = (critical / total * 100) if total > 0 else 0
            evidence.append(f"{critical} functions with critical complexity (20+) = {pct:.1f}% of codebase")
        
        if high > 0:
            pct = (high / total * 100) if total > 0 else 0
            evidence.append(f"{high} functions with high complexity (10-19) = {pct:.1f}% of codebase")
        
        if max_c > 0:
            evidence.append(f"Maximum complexity detected: {max_c}")
        
        evidence.append(f"Average complexity: {avg:.2f}")
        
        # Determine verdict and conclusion
        if max_c > 100:
            verdict = VerdictLevel.CRITICAL
            conclusion = "This codebase contains functions too complex for humans to safely modify.\nRefactoring is not optional—it's mandatory for survival."
        elif critical > 20 or max_c > 50:
            verdict = VerdictLevel.UNSUSTAINABLE
            conclusion = "Complexity has reached dangerous levels.\nNew features will take 3x longer to implement safely."
        elif critical > 5 or max_c > 30:
            verdict = VerdictLevel.CONCERNING
            conclusion = "Complexity is growing unchecked.\nAddress the worst offenders before they metastasize."
        elif avg < 5 and max_c < 20:
            verdict = VerdictLevel.EXCELLENT
            conclusion = "This codebase is a pleasure to work with.\nComplexity is well-managed and maintainability is high."
        else:
            verdict = VerdictLevel.SUSTAINABLE
            conclusion = "Complexity is manageable but monitor the high-complexity functions.\nPrevent them from growing further."
        
        OrcVerdict.format_verdict(verdict, evidence, conclusion)
    
    @staticmethod
    def dead_code_verdict(stats: Dict[str, Any]) -> None:
        """Generate verdict for dead code analysis."""
        total_funcs = stats.get('total_functions_analyzed', 0)
        dead = stats.get('total_potentially_unused', 0)
        safe_delete = stats.get('safe_to_delete_count', 0)
        
        if total_funcs == 0:
            return
        
        dead_pct = (dead / total_funcs * 100)
        
        evidence = []
        evidence.append(f"{dead} potentially unused functions out of {total_funcs} analyzed ({dead_pct:.1f}%)")
        
        if safe_delete > 0:
            evidence.append(f"{safe_delete} functions are safe to delete immediately")
        
        # Determine verdict
        if dead_pct > 40:
            verdict = VerdictLevel.CRITICAL
            conclusion = "This codebase is drowning in dead code.\nOver 40% of functions appear unused—confusion and bugs are inevitable."
        elif dead_pct > 25:
            verdict = VerdictLevel.UNSUSTAINABLE
            conclusion = "Dead code is accumulating faster than living code.\nDevelopers waste time reading and maintaining code that does nothing."
        elif dead_pct > 15:
            verdict = VerdictLevel.CONCERNING
            conclusion = "Dead code is starting to pile up.\nSchedule a cleanup sprint before it becomes unmanageable."
        elif dead_pct < 5:
            verdict = VerdictLevel.EXCELLENT
            conclusion = "This codebase is lean and well-maintained.\nDead code is promptly removed, keeping cognitive load low."
        else:
            verdict = VerdictLevel.SUSTAINABLE
            conclusion = "Dead code is present but not overwhelming.\nRegular cleanup will keep it under control."
        
        OrcVerdict.format_verdict(verdict, evidence, conclusion)
    
    @staticmethod
    def hotspots_verdict(hotspots: Dict[str, Any]) -> None:
        """Generate verdict for hotspot analysis."""
        complexity_hotspots = hotspots.get('complexity_hotspots', [])
        large_files = hotspots.get('large_files', [])
        
        evidence = []
        
        # Complexity hotspots
        if complexity_hotspots:
            top = complexity_hotspots[0]
            evidence.append(f"'{top.get('file_path', 'unknown')}' has {top.get('complex_functions', 0)} complex functions")
            
            if len(complexity_hotspots) >= 3:
                evidence.append(f"{len(complexity_hotspots)} files are complexity hotspots")
        
        # Large files
        if large_files:
            top = large_files[0]
            lines = top.get('loc', 0)
            evidence.append(f"Largest file has {lines:,} lines")
            
            mega_files = [f for f in large_files if f.get('loc', 0) > 10000]
            if mega_files:
                evidence.append(f"{len(mega_files)} files exceed 10,000 lines")
        
        # Determine verdict
        if len(complexity_hotspots) >= 5 or any(f.get('loc', 0) > 50000 for f in large_files):
            verdict = VerdictLevel.CRITICAL
            conclusion = "Multiple files are beyond human comprehension.\nThese files will become bottlenecks for every feature."
        elif len(complexity_hotspots) >= 3 or any(f.get('loc', 0) > 20000 for f in large_files):
            verdict = VerdictLevel.UNSUSTAINABLE
            conclusion = "Several files have become dumping grounds for complexity.\nSplit them before they become unmaintainable."
        elif len(complexity_hotspots) >= 1:
            verdict = VerdictLevel.CONCERNING
            conclusion = "Some files are accumulating complexity.\nWatch these files closely and refactor when they grow."
        else:
            verdict = VerdictLevel.SUSTAINABLE
            conclusion = "No severe hotspots detected.\nComplexity is reasonably distributed across the codebase."
        
        OrcVerdict.format_verdict(verdict, evidence, conclusion)
    
    @staticmethod
    def overall_verdict(analysis: Dict[str, Any]) -> None:
        """Generate overall codebase verdict."""
        # Gather metrics
        complexity = analysis.get('complexity', {})
        dead_code = analysis.get('dead_code', {})
        hotspots = analysis.get('hotspots', {})
        
        avg_complexity = complexity.get('average_complexity', 0)
        max_complexity = complexity.get('max_complexity', 0)
        critical_count = complexity.get('critical_count', 0)
        
        dead_pct = 0
        if dead_code.get('total_functions_analyzed', 0) > 0:
            dead_pct = (dead_code.get('total_potentially_unused', 0) / 
                       dead_code.get('total_functions_analyzed', 1) * 100)
        
        hotspot_count = len(hotspots.get('complexity_hotspots', []))
        
        evidence = []
        
        # Complexity evidence
        if critical_count > 0:
            evidence.append(f"{critical_count} functions with critical complexity")
        
        # Dead code evidence
        if dead_pct > 15:
            evidence.append(f"{dead_pct:.0f}% of codebase appears unused")
        
        # Hotspots evidence
        if hotspot_count > 0:
            evidence.append(f"{hotspot_count} files act as complexity choke points")
        
        # Test coverage (if available)
        test_cov = analysis.get('test_coverage', 0)
        if test_cov < 50:
            evidence.append("Tests do not cover failure paths")
        
        # Determine overall verdict
        issues = sum([
            1 if max_complexity > 50 else 0,
            1 if dead_pct > 25 else 0,
            1 if hotspot_count > 3 else 0,
            1 if critical_count > 20 else 0
        ])
        
        if issues >= 3:
            verdict = VerdictLevel.CRITICAL
            conclusion = "This codebase is in crisis.\nRefactoring must begin immediately or development will grind to a halt."
        elif issues >= 2:
            verdict = VerdictLevel.UNSUSTAINABLE
            conclusion = "This codebase will resist iteration after the next major version.\nTechnical debt is compounding faster than features ship."
        elif issues >= 1:
            verdict = VerdictLevel.CONCERNING
            conclusion = "Warning signs are emerging.\nAddress these issues now while they're still manageable."
        elif avg_complexity < 5 and dead_pct < 5:
            verdict = VerdictLevel.EXCELLENT
            conclusion = "This codebase is a model of maintainability.\nKeep doing what you're doing."
        else:
            verdict = VerdictLevel.SUSTAINABLE
            conclusion = "This codebase is healthy enough to evolve.\nMaintain vigilance and address problems as they appear."
        
        OrcVerdict.format_verdict(verdict, evidence, conclusion)
