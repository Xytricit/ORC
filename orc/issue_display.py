def format_security_issue(priority, title, description):
    return f"""{priority}:

{title}

{description}
"""

def format_issue_list(issues):
    """Format multiple issues with consistent spacing"""
    return "\n\n".join(
        format_security_issue(i['priority'], i['title'], i['desc']) 
        for i in issues
    )

# Example usage
if __name__ == "__main__":
    issues = [
        {
            'priority': 'CRITICAL',
            'title': 'SQL Injection Vulnerability',
            'desc': 'Unsanitized input in user authentication form'
        },
        {
            'priority': 'HIGH',
            'title': 'Missing Rate Limiting',
            'desc': 'Login endpoint vulnerable to brute force attacks'
        }
    ]
    print(format_issue_list(issues))