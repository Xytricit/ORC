from orc.response_formatter import format_analysis_response

def format_query_response(query, result_type, data):
    """Format response based on result type"""
    if result_type == "list":
        items = "\n".join(f"  • {item}" for item in data[:10])
        return f"\n{items}\n"
    
    elif result_type == "analysis":
        return format_analysis_response(
            data['title'], 
            data['content'], 
            data.get('metadata')
        )
    
    elif result_type == "code":
        return f"\n{data['code']}\n"

# Example usage
if __name__ == "__main__":
    # Example list response
    print(format_query_response("find all controllers", "list", [
        "user_controller.py",
        "auth_controller.py", 
        "product_controller.py",
        "order_controller.py",
        "payment_controller.py",
        "notification_controller.py",
        "analytics_controller.py",
        "settings_controller.py",
        "admin_controller.py",
        "api_controller.py",
        "health_controller.py"
    ]))