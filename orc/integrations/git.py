"""Git integration for ORC - Pull Request analysis and change impact assessment."""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tempfile
import json


@dataclass
class GitChange:
    """Represents a single change in a Git diff."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    line_numbers: List[int]  # Lines that were changed
    content_before: Optional[str] = None
    content_after: Optional[str] = None


@dataclass
class PRAnalysis:
    """Represents the analysis of a pull request."""
    changes: List[GitChange]
    complexity_changes: Dict[str, int]  # File path -> change in complexity
    potential_issues: List[str]
    impact_summary: str
    risk_level: str  # 'low', 'medium', 'high', 'critical'


class GitIntegration:
    """Provides Git integration for ORC, including PR analysis."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"{repo_path} is not a Git repository")

    def get_current_branch(self) -> str:
        """Get the current Git branch."""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def get_diff_between_branches(self, base_branch: str = "main", 
                                 feature_branch: str = None) -> List[GitChange]:
        """Get the diff between two branches."""
        if feature_branch is None:
            feature_branch = self.get_current_branch()

        # Get the diff
        result = subprocess.run(
            ["git", "diff", f"{base_branch}...{feature_branch}", "--unified=0"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Git diff failed: {result.stderr}")

        return self._parse_diff(result.stdout)

    def get_changed_files(self, base_branch: str = "main", 
                         feature_branch: str = None) -> List[str]:
        """Get list of files changed between branches."""
        if feature_branch is None:
            feature_branch = self.get_current_branch()

        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...{feature_branch}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Git diff --name-only failed: {result.stderr}")

        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

    def analyze_pull_request(self, base_branch: str = "main", 
                           feature_branch: str = None) -> PRAnalysis:
        """Analyze a pull request for potential issues and impact."""
        if feature_branch is None:
            feature_branch = self.get_current_branch()

        # Get changed files
        changed_files = self.get_changed_files(base_branch, feature_branch)
        
        # Get detailed diff information
        changes = self.get_diff_between_branches(base_branch, feature_branch)

        # Analyze complexity changes (simplified for this implementation)
        complexity_changes = self._analyze_complexity_changes(changes)
        
        # Identify potential issues
        potential_issues = self._identify_potential_issues(changes)
        
        # Generate impact summary
        impact_summary = self._generate_impact_summary(changes, potential_issues)
        
        # Determine risk level
        risk_level = self._determine_risk_level(potential_issues, len(changes))

        return PRAnalysis(
            changes=changes,
            complexity_changes=complexity_changes,
            potential_issues=potential_issues,
            impact_summary=impact_summary,
            risk_level=risk_level
        )

    def _parse_diff(self, diff_output: str) -> List[GitChange]:
        """Parse Git diff output into structured changes."""
        changes = []
        lines = diff_output.split('\n')
        
        current_file = None
        current_change_type = None
        current_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for file header
            if line.startswith('diff --git'):
                # Process previous file if exists
                if current_file:
                    changes.append(GitChange(
                        file_path=current_file,
                        change_type=current_change_type,
                        line_numbers=current_lines
                    ))
                
                # Extract file path from diff header
                # Format: diff --git a/file.py b/file.py
                parts = line.split()
                if len(parts) >= 3:
                    file_part = parts[2]  # a/file.py
                    current_file = file_part[2:] if file_part.startswith('a/') else file_part
                    current_change_type = 'modified'
                    current_lines = []
            
            # Check for new file
            elif line.startswith('new file mode'):
                current_change_type = 'added'
            
            # Check for deleted file
            elif line.startswith('deleted file mode'):
                current_change_type = 'deleted'
            
            # Check for hunk header
            elif line.startswith('@@'):
                # Extract line numbers from hunk header
                # Format: @@ -start_line,count +end_line,count @@
                import re
                match = re.search(r'@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@', line)
                if match:
                    start_line = int(match.group(1))
                    line_count = int(match.group(2)) if match.group(2) else 1
                    for line_num in range(start_line, start_line + line_count):
                        current_lines.append(line_num)
            
            i += 1

        # Process last file
        if current_file:
            changes.append(GitChange(
                file_path=current_file,
                change_type=current_change_type,
                line_numbers=current_lines
            ))

        return changes

    def _analyze_complexity_changes(self, changes: List[GitChange]) -> Dict[str, int]:
        """Analyze changes to estimate complexity impact."""
        complexity_changes = {}
        
        for change in changes:
            # For this simplified implementation, we'll estimate based on lines changed
            # In a real implementation, we would analyze the actual code changes
            complexity_changes[change.file_path] = len(change.line_numbers) * 2  # Rough estimate
        
        return complexity_changes

    def _identify_potential_issues(self, changes: List[GitChange]) -> List[str]:
        """Identify potential issues in the changes."""
        issues = []
        
        for change in changes:
            file_path = change.file_path
            
            # Check for critical files
            if any(critical in file_path.lower() for critical in ['auth', 'security', 'payment', 'config']):
                issues.append(f"Critical file modified: {file_path}")
            
            # Check for large changes
            if len(change.line_numbers) > 100:
                issues.append(f"Large change in {file_path} ({len(change.line_numbers)} lines)")
            
            # Check for test files
            if 'test' not in file_path.lower() and len(change.line_numbers) > 10:
                issues.append(f"Significant code change without apparent test changes: {file_path}")
        
        return issues

    def _generate_impact_summary(self, changes: List[GitChange], 
                                potential_issues: List[str]) -> str:
        """Generate a summary of the impact."""
        total_files = len(changes)
        total_lines = sum(len(change.line_numbers) for change in changes)
        
        summary = f"PR affects {total_files} files with {total_lines} lines changed. "
        
        if potential_issues:
            summary += f"Identified {len(potential_issues)} potential issues."
        else:
            summary += "No major issues detected."
        
        return summary

    def _determine_risk_level(self, potential_issues: List[str], 
                             total_changes: int) -> str:
        """Determine the risk level of the changes."""
        issue_count = len(potential_issues)
        
        if issue_count >= 5 or total_changes > 200:
            return 'critical'
        elif issue_count >= 3 or total_changes > 100:
            return 'high'
        elif issue_count >= 1 or total_changes > 50:
            return 'medium'
        else:
            return 'low'

    def get_commit_history(self, file_path: str, limit: int = 10) -> List[Dict]:
        """Get commit history for a specific file."""
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--pretty=format:{\"hash\":\"%H\",\"author\":\"%an\",\"date\":\"%ad\",\"message\":\"%s\"}", "--", file_path],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        # Parse the commit history
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    # This is a simplified parsing - in reality, we'd need more robust JSON parsing
                    commit_info = {
                        "hash": line[:8] if len(line) > 8 else line,
                        "author": "Unknown",
                        "date": "Unknown",
                        "message": line
                    }
                    commits.append(commit_info)
                except:
                    continue
        
        return commits

    def get_file_at_revision(self, file_path: str, revision: str = "HEAD") -> Optional[str]:
        """Get the content of a file at a specific revision."""
        result = subprocess.run(
            ["git", "show", f"{revision}:{file_path}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return None
        
        return result.stdout


def analyze_pull_request(repo_path: str = ".", base_branch: str = "main", 
                       feature_branch: str = None) -> PRAnalysis:
    """Public function to analyze a pull request."""
    git_integration = GitIntegration(repo_path)
    return git_integration.analyze_pull_request(base_branch, feature_branch)