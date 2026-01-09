def format_code_location(file, line):
    """Format code location reference"""
    return f"{file} at {line} lines"

def format_analysis_response(title, content, metadata=None):
    """Format a standard analysis response"""
    response = f"\n{title}\n\n{content}\n"
    if metadata:
        response += "\n" + "\n".join(f"  {k}: {v}" for k, v in metadata.items())
    return response + "\n─────────────────────────────────────────────────────\n"

# Example
if __name__ == "__main__":
    print(format_analysis_response(
        "Found 4 security concerns in authentication system.",
        "HIGH PRIORITY:\n\nLogin endpoint lacks rate limiting...",
        {"Total Issues": 4, "Critical": 1, "High": 2}
    ))