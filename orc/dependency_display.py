def format_caller_list(function_id, callers, impact_data):
    return f"""
Function {function_id} is called from {len(callers)} locations:

{chr(10).join(f"  • {caller}" for caller in callers[:10])}

Total call frequency: {impact_data['frequency']}/day
Peak load: {impact_data['peak_context']}
Impact scope: {impact_data['scope']}
"""

# Example usage
if __name__ == "__main__":
    callers = [
        "user_service.py:120",
        "auth_controller.py:45",
        "data_processor.py:210",
        "notification_service.py:78",
        "analytics_tracker.py:300"
    ]
    impact_data = {
        'frequency': 15000,
        'peak_context': 'During user login高峰期',
        'scope': 'Affects 3 major services'
    }
    print(format_caller_list("validate_user_session", callers, impact_data))