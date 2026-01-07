"""
Sample codebase for testing ORC
Includes various patterns: dead code, complexity, circular deps
"""

# Used function - should NOT be flagged as dead
def calculate_total(items):
    """Calculate sum of items"""
    total = 0
    for item in items:
        total += item
    return total

# Unused function - SHOULD be flagged as dead code
def unused_helper():
    """This function is never called"""
    return "I'm never used"

# Complex function - SHOULD be flagged for high complexity
def complex_business_logic(user, permissions, resource, context):
    """
    Overly complex function with high cyclomatic complexity
    """
    if user is None:
        return False
    
    if not user.is_active:
        return False
    
    if user.is_admin:
        return True
    
    if permissions is None:
        return False
    
    for perm in permissions:
        if perm.resource_type == resource.type:
            if perm.level == "read":
                if context.action == "read":
                    return True
            elif perm.level == "write":
                if context.action in ["read", "write"]:
                    return True
            elif perm.level == "admin":
                return True
    
    if resource.is_public:
        if context.action == "read":
            return True
    
    if resource.owner_id == user.id:
        return True
    
    if user.group_id:
        if resource.group_id == user.group_id:
            if context.action != "delete":
                return True
    
    return False

# Function that calls another - establishes call graph
def process_order(order_items):
    """Process an order"""
    total = calculate_total(order_items)
    return {
        'total': total,
        'status': 'processed'
    }

# Another unused function
def old_deprecated_function():
    """Deprecated and unused"""
    pass

# Exported but never imported elsewhere
def public_api_unused():
    """Public API that nothing uses"""
    return "exported but unused"

class UnusedClass:
    """Class that is never instantiated"""
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value

# Actually used class
class Order:
    """Order class"""
    def __init__(self, items):
        self.items = items
        self.total = calculate_total(items)