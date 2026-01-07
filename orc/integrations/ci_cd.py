"""CI/CD integration helpers for ORC - enables automated code analysis in pipelines."""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import tempfile


@dataclass
class AnalysisResult:
    """Represents the result of an ORC analysis."""
    tool: str  # 'deadcode', 'complexity', 'metrics', etc.
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: str
    config_used: Dict[str, Any]


@dataclass
class CIPipelineReport:
    """Represents a complete CI pipeline report."""
    repository: str
    branch: str
    commit_sha: str
    analysis_results: List[AnalysisResult]
    issues_found: int
    status: str  # 'pass', 'fail', 'warning'
    recommendations: List[str]
    created_at: str


class CICDIntegration:
    """Provides CI/CD integration for ORC analysis."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.orc_executable = self._find_orc_executable()

    def _find_orc_executable(self) -> Optional[str]:
        """Find the ORC executable in the environment."""
        # Try different possible locations for the ORC executable
        possible_paths = [
            "orc",  # In PATH
            str(Path(__file__).parent.parent / "run_orc.py"),  # Local script
            "python -m orc",  # Python module
        ]

        for path in possible_paths:
            try:
                result = subprocess.run(
                    f"{path} --help",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        return None

    def run_analysis_in_ci(self, analysis_types: List[str] = None) -> CIPipelineReport:
        """Run ORC analysis as part of a CI pipeline."""
        if analysis_types is None:
            analysis_types = ['deadcode', 'complexity', 'metrics']

        if not self.orc_executable:
            raise RuntimeError("ORC executable not found. Please install ORC before running in CI.")

        # Get repository info
        repo_info = self._get_repo_info()
        
        analysis_results = []
        total_issues = 0
        recommendations = []

        # Run each analysis type
        for analysis_type in analysis_types:
            result = self._run_single_analysis(analysis_type)
            if result:
                analysis_results.append(result)
                total_issues += len(result.findings)
                if result.summary.get('recommendations'):
                    recommendations.extend(result.summary['recommendations'])

        # Determine overall status
        status = 'pass'
        if total_issues > 50:  # Arbitrary threshold
            status = 'fail'
        elif total_issues > 10:
            status = 'warning'

        from datetime import datetime
        report = CIPipelineReport(
            repository=repo_info['repository'],
            branch=repo_info['branch'],
            commit_sha=repo_info['commit_sha'],
            analysis_results=analysis_results,
            issues_found=total_issues,
            status=status,
            recommendations=recommendations,
            created_at=datetime.now().isoformat()
        )

        return report

    def _get_repo_info(self) -> Dict[str, str]:
        """Get repository information."""
        try:
            # Get repository name
            origin_url = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            repo_name = origin_url.split('/')[-1].replace('.git', '')
            
            # Get current branch
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            # Get current commit SHA
            commit_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()[:8]  # Short SHA
            
            return {
                'repository': repo_name,
                'branch': branch,
                'commit_sha': commit_sha
            }
        except subprocess.CalledProcessError:
            # Fallback if not in a git repo
            return {
                'repository': 'unknown',
                'branch': 'unknown',
                'commit_sha': 'unknown'
            }

    def _run_single_analysis(self, analysis_type: str) -> Optional[AnalysisResult]:
        """Run a single type of analysis."""
        if not self.orc_executable:
            return None

        try:
            # Create a temporary config file for CI
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_content = {
                    'ignore': [
                        'tests/*',
                        'test_*.py',
                        'conftest.py',
                        'venv/*',
                        '.venv/*',
                        'node_modules/*',
                        '.git/*',
                        '__pycache__/*',
                        '*.egg-info/*'
                    ],
                    'dynamic_patterns': ['eval', 'exec', 'getattr', 'hasattr', 'importlib']
                }
                json.dump(config_content, f)
                temp_config_path = f.name

            # Run the analysis
            cmd_parts = self.orc_executable.split()
            cmd = cmd_parts + [analysis_type, '--config', temp_config_path]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Clean up temp config
            os.unlink(temp_config_path)

            if result.returncode == 0:
                # Parse the output based on analysis type
                findings, summary = self._parse_analysis_output(result.stdout, analysis_type)
                
                return AnalysisResult(
                    tool=analysis_type,
                    findings=findings,
                    summary=summary,
                    timestamp=self._get_timestamp(),
                    config_used=config_content
                )
            else:
                print(f"Warning: {analysis_type} analysis failed with error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"Warning: {analysis_type} analysis timed out")
            return None
        except Exception as e:
            print(f"Warning: {analysis_type} analysis error: {str(e)}")
            return None

    def _parse_analysis_output(self, output: str, analysis_type: str) -> tuple[List[Dict], Dict]:
        """Parse the output of an analysis command."""
        findings = []
        summary = {}

        if analysis_type == 'deadcode':
            # Parse dead code output
            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith('[D-'):
                    # Parse dead code findings like [D-01] src/auth.py - unused_function
                    import re
                    match = re.match(r'\[(D-\d+)\]\s+(.+?)\s*-\s*(.+)', line)
                    if match:
                        finding_id, file_path, function_name = match.groups()
                        findings.append({
                            'id': finding_id,
                            'file': file_path.strip(),
                            'function': function_name.strip(),
                            'type': 'dead_code'
                        })
        
        elif analysis_type == 'complexity':
            # Parse complexity output
            lines = output.strip().split('\n')
            for line in lines:
                if 'O(' in line and ')' in line:
                    # Look for complexity patterns like O(n²), O(n³), etc.
                    import re
                    complexity_pattern = r'O\([^)]+\)'
                    complexities = re.findall(complexity_pattern, line)
                    if complexities:
                        findings.append({
                            'function': 'unknown',  # Would need more detailed parsing
                            'complexity': complexities[0],
                            'type': 'complexity'
                        })
        
        elif analysis_type == 'metrics':
            # Parse metrics output
            summary = {
                'total_files': 0,
                'total_functions': 0,
                'total_lines': 0,
                'avg_complexity': 0.0
            }

        return findings, summary

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def generate_ci_report(self, report: CIPipelineReport, output_format: str = 'json') -> str:
        """Generate a CI report in the specified format."""
        if output_format == 'json':
            return json.dumps(self._report_to_dict(report), indent=2)
        elif output_format == 'markdown':
            return self._report_to_markdown(report)
        elif output_format == 'text':
            return self._report_to_text(report)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _report_to_dict(self, report: CIPipelineReport) -> Dict:
        """Convert report to dictionary."""
        return {
            'repository': report.repository,
            'branch': report.branch,
            'commit': report.commit_sha,
            'status': report.status,
            'issues_found': report.issues_found,
            'analysis_results': [
                {
                    'tool': r.tool,
                    'findings_count': len(r.findings),
                    'findings': r.findings,
                    'summary': r.summary
                } for r in report.analysis_results
            ],
            'recommendations': report.recommendations,
            'created_at': report.created_at
        }

    def _report_to_markdown(self, report: CIPipelineReport) -> str:
        """Convert report to markdown format."""
        md = f"# ORC Analysis Report\n\n"
        md += f"**Repository**: {report.repository}\n\n"
        md += f"**Branch**: {report.branch}\n"
        md += f"**Commit**: {report.commit_sha}\n\n"
        md += f"## Status: {report.status.upper()}\n\n"
        md += f"**Issues Found**: {report.issues_found}\n\n"

        for result in report.analysis_results:
            md += f"### {result.tool.title()} Analysis\n\n"
            md += f"- Findings: {len(result.findings)}\n"
            if result.findings:
                md += "#### Top Findings:\n"
                for finding in result.findings[:5]:  # Show top 5
                    md += f"- {finding}\n"
                if len(result.findings) > 5:
                    md += f"... and {len(result.findings) - 5} more\n"
            md += "\n"

        if report.recommendations:
            md += "## Recommendations\n\n"
            for rec in report.recommendations[:10]:  # Show top 10
                md += f"- {rec}\n"

        return md

    def _report_to_text(self, report: CIPipelineReport) -> str:
        """Convert report to plain text format."""
        text = f"ORC Analysis Report\n"
        text += f"=" * 50 + "\n"
        text += f"Repository: {report.repository}\n"
        text += f"Branch: {report.branch}\n"
        text += f"Commit: {report.commit_sha}\n"
        text += f"Status: {report.status.upper()}\n"
        text += f"Issues Found: {report.issues_found}\n\n"

        for result in report.analysis_results:
            text += f"{result.tool.title()} Analysis:\n"
            text += f"  Findings: {len(result.findings)}\n"
            if result.findings:
                text += "  Top Findings:\n"
                for finding in result.findings[:5]:  # Show top 5
                    text += f"    - {finding}\n"
                if len(result.findings) > 5:
                    text += f"    ... and {len(result.findings) - 5} more\n"
            text += "\n"

        if report.recommendations:
            text += "Recommendations:\n"
            for rec in report.recommendations[:10]:  # Show top 10
                text += f"  - {rec}\n"

        return text

    def should_fail_pipeline(self, report: CIPipelineReport, 
                           failure_threshold: int = 10) -> bool:
        """Determine if the pipeline should fail based on the report."""
        return report.issues_found > failure_threshold

    def export_results(self, report: CIPipelineReport, 
                      output_path: str, format: str = 'json') -> None:
        """Export analysis results to a file."""
        content = self.generate_ci_report(report, format)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def run_ci_analysis(project_path: str = ".", 
                   analysis_types: List[str] = None,
                   output_format: str = 'json',
                   output_path: str = None) -> CIPipelineReport:
    """Run ORC analysis in CI/CD pipeline and return report."""
    if analysis_types is None:
        analysis_types = ['deadcode', 'complexity', 'metrics']
    
    ci_integration = CICDIntegration(project_path)
    report = ci_integration.run_analysis_in_ci(analysis_types)
    
    # Export if path provided
    if output_path:
        ci_integration.export_results(report, output_path, output_format)
    
    return report


def should_pipeline_fail(report: CIPipelineReport, threshold: int = 10) -> bool:
    """Helper function to determine if pipeline should fail."""
    ci_integration = CICDIntegration()
    return ci_integration.should_fail_pipeline(report, threshold)