def format_dead_code_findings(findings):
    """Format dead code findings with IDs"""
    output = []
    for idx, finding in enumerate(findings, 1):
        output.append(
            f"[D-{idx:02d}] {finding['file']} - {finding['function']}"
        )
    return "\n".join(output)

def format_file_list(category, files):
    """Format file lists with counts"""
    return f"""
{category} ({len(files)} files):
{chr(10).join(f"  • {f}" for f in files[:10])}
{"  ... and " + str(len(files) - 10) + " more" if len(files) > 10 else ""}
"""

# Example usage
if __name__ == "__main__":
    findings = [
        {'file': 'utils.py', 'function': 'old_hash_function'},
        {'file': 'auth.py', 'function': 'deprecated_login'},
        {'file': 'models.py', 'function': 'unused_model_method'}
    ]
    print(format_dead_code_findings(findings))
    
    files = [f"file_{i}.py" for i in range(1, 15)]
    print(format_file_list("Python Files", files))