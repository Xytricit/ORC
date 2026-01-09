def format_recommendation(title, description, details):
    return f"""
{title}

{description}

{details}
"""

def format_alternative_approaches(alternatives):
    """Format alternative implementation approaches"""
    return "Alternative approaches:\n" + "\n".join(
        f"- {alt['name']} ({alt['description']})"
        for alt in alternatives
    )

# Example usage
if __name__ == "__main__":
    print(format_recommendation(
        "Migrate to JWT authentication",
        "Current session-based auth is causing scalability issues",
        "Implementation would involve creating token-based system with proper refresh mechanisms"
    ))
    
    alternatives = [
        {'name': 'Redis-based sessions', 'description': 'Keep current approach but use Redis for scalability'},
        {'name': 'OAuth 2.0 integration', 'description': 'Use external identity provider'},
        {'name': 'Custom token system', 'description': 'Build in-house token solution'}
    ]
    print(format_alternative_approaches(alternatives))