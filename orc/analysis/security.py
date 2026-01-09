"""Security scanner for ORC - Identifies potential security vulnerabilities in code."""

import ast
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import os


@dataclass
class SecurityIssue:
    """Represents a security issue found in code."""
    rule_id: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str


class SecurityScanner:
    """Scans code for potential security vulnerabilities."""

    def __init__(self):
        self.security_rules = self._define_security_rules()

    def _define_security_rules(self) -> Dict[str, Dict]:
        """Define security rules to check for."""
        return {
            'hardcoded_secrets': {
                'pattern': r'(["\'](?:password|secret|token|key|api_key|db_password)["\'][\s]*[=:][\s]*["\'][^"\']+["\'])',
                'severity': 'critical',
                'description': 'Hardcoded secret detected',
                'recommendation': 'Use environment variables or secure secret management'
            },
            'insecure_deserialization': {
                'pattern': r'(?:pickle\.loads?|eval|exec)\s*\(',
                'severity': 'high',
                'description': 'Insecure deserialization or code execution',
                'recommendation': 'Avoid using eval(), exec(), or pickle for untrusted data'
            },
            'sql_injection': {
                'pattern': r'cursor\.execute\s*\([^"\'"]*[\+\s]*["\'].*{.*}.*["\'][\+\s]*[^"\'"]*\)',
                'severity': 'high',
                'description': 'Potential SQL injection vulnerability',
                'recommendation': 'Use parameterized queries instead of string formatting'
            },
            'command_injection': {
                'pattern': r'(?:subprocess\.call|os\.system|os\.popen)\s*\([^"\'"]*[\+\s]*[^"\'"]*\)',
                'severity': 'high',
                'description': 'Potential command injection vulnerability',
                'recommendation': 'Validate and sanitize all inputs before using in system commands'
            },
            'path_traversal': {
                'pattern': r'open\s*\([^"\'"]*[\+\s]*[^"\'"]*\)',
                'severity': 'medium',
                'description': 'Potential path traversal vulnerability',
                'recommendation': 'Validate file paths and use os.path.join safely'
            },
            'weak_crypto': {
                'pattern': r'(?:hashlib\.(md5|sha1)|CRYPT_MD5)',
                'severity': 'medium',
                'description': 'Use of weak cryptographic algorithm',
                'recommendation': 'Use stronger algorithms like SHA-256 or SHA-3'
            },
            'debug_statements': {
                'pattern': r'(?:print|console\.log|pdb\.set_trace|breakpoint\(\))',
                'severity': 'low',
                'description': 'Debug statement detected',
                'recommendation': 'Remove debug statements before production'
            }
        }

    def scan_file(self, file_path: str) -> List[SecurityIssue]:
        """Scan a single file for security issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for pattern-based issues
            for rule_id, rule in self.security_rules.items():
                matches = re.finditer(rule['pattern'], content, re.IGNORECASE)
                for match in matches:
                    # Find the line number
                    line_start = content[:match.start()].count('\n') + 1
                    code_snippet = lines[line_start - 1].strip() if line_start <= len(lines) else ""
                    
                    issues.append(SecurityIssue(
                        rule_id=rule_id,
                        severity=rule['severity'],
                        description=rule['description'],
                        file_path=file_path,
                        line_number=line_start,
                        code_snippet=code_snippet,
                        recommendation=rule['recommendation']
                    ))
            
            # AST-based checks for more sophisticated patterns
            try:
                tree = ast.parse(content)
                ast_issues = self._scan_ast(tree, file_path, lines)
                issues.extend(ast_issues)
            except SyntaxError:
                # If the file isn't valid Python, skip AST analysis
                pass
                
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
        
        return issues

    def _scan_ast(self, tree: ast.AST, file_path: str, lines: List[str]) -> List[SecurityIssue]:
        """Scan AST for security issues."""
        issues = []
        
        for node in ast.walk(tree):
            # Check for eval() usage
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    line_no = node.lineno
                    code_snippet = lines[line_no - 1] if line_no <= len(lines) else ""
                    issues.append(SecurityIssue(
                        rule_id='insecure_deserialization',
                        severity='high',
                        description='Use of eval() function',
                        file_path=file_path,
                        line_number=line_no,
                        code_snippet=code_snippet,
                        recommendation='Avoid using eval(); use ast.literal_eval() for simple data structures'
                    ))
            
            # Check for hardcoded secrets in assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if any(secret_word in target.id.lower() for secret_word in 
                              ['password', 'secret', 'token', 'key', 'api_key', 'db_password']):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                line_no = node.lineno
                                code_snippet = lines[line_no - 1] if line_no <= len(lines) else ""
                                issues.append(SecurityIssue(
                                    rule_id='hardcoded_secrets',
                                    severity='critical',
                                    description='Hardcoded secret in variable assignment',
                                    file_path=file_path,
                                    line_number=line_no,
                                    code_snippet=code_snippet,
                                    recommendation='Use environment variables or secure secret management'
                                ))
            
            # Check for weak hashing algorithms
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if (node.func.attr in ['md5', 'sha1'] and 
                    isinstance(node.func.value, ast.Name) and 
                    node.func.value.id == 'hashlib'):
                    line_no = node.lineno
                    code_snippet = lines[line_no - 1] if line_no <= len(lines) else ""
                    issues.append(SecurityIssue(
                        rule_id='weak_crypto',
                        severity='medium',
                        description='Use of weak cryptographic algorithm',
                        file_path=file_path,
                        line_number=line_no,
                        code_snippet=code_snippet,
                        recommendation='Use stronger algorithms like SHA-256 or SHA-3'
                    ))
        
        return issues

    def scan_directory(self, directory_path: str, extensions: List[str] = ['.py']) -> List[SecurityIssue]:
        """Scan an entire directory for security issues."""
        issues = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip common directories that shouldn't be scanned
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    file_issues = self.scan_file(file_path)
                    issues.extend(file_issues)
        
        return issues

    def generate_security_report(self, issues: List[SecurityIssue]) -> Dict:
        """Generate a security report from the found issues."""
        report = {
            'total_issues': len(issues),
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'by_rule': {},
            'files_affected': set(),
            'issues': []
        }
        
        for issue in issues:
            # Count by severity
            report['by_severity'][issue.severity] += 1
            
            # Count by rule
            if issue.rule_id not in report['by_rule']:
                report['by_rule'][issue.rule_id] = 0
            report['by_rule'][issue.rule_id] += 1
            
            # Track affected files
            report['files_affected'].add(issue.file_path)
            
            # Add issue details
            report['issues'].append({
                'rule_id': issue.rule_id,
                'severity': issue.severity,
                'description': issue.description,
                'file_path': issue.file_path,
                'line_number': issue.line_number,
                'code_snippet': issue.code_snippet,
                'recommendation': issue.recommendation
            })
        
        report['files_affected'] = list(report['files_affected'])
        return report

    def print_security_summary(self, issues: List[SecurityIssue]):
        """Print a summary of security issues to console."""
        if not issues:
            print("No security issues found!")
            return
        
        print(f"\n🚨 Found {len(issues)} security issues:")
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                issue_list = by_severity[severity]
                print(f"\n{severity.upper()} ({len(issue_list)} issues):")
                for issue in issue_list[:5]:  # Show first 5 of each severity
                    print(f"  • {issue.file_path}:{issue.line_number} - {issue.description}")
                if len(issue_list) > 5:
                    print(f"    ... and {len(issue_list) - 5} more")


def scan_project_security(directory_path: str) -> Dict:
    """Public function to scan a project for security issues."""
    scanner = SecurityScanner()
    issues = scanner.scan_directory(directory_path)
    report = scanner.generate_security_report(issues)
    scanner.print_security_summary(issues)
    return report