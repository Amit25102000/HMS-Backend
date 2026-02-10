"""
Role-based menu configuration for dashboards
Defines which menu items and actions are available to each role
"""

# Menu configuration for each role
ROLE_MENU_CONFIG = {
    'SUPER_ADMIN': {
        'dashboard': True,
        'patients': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'appointments': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'doctors': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'prescriptions': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'inventory': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'billing': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'reports': {'view': True, 'create': True},
        'users': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'settings': True,
    },
    'ADMIN': {
        'dashboard': True,
        'patients': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'appointments': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'doctors': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'prescriptions': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'inventory': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'billing': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'reports': {'view': True, 'create': True},
        'users': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'settings': True,
    },
    'DOCTOR': {
        'dashboard': True,
        'patients': {'view': True, 'create': False, 'edit': False, 'delete': False},
        'appointments': {'view': True, 'create': False, 'edit': True, 'delete': False},
        'prescriptions': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'inventory': {'view': True, 'create': False, 'edit': False, 'delete': False},
        'profile': {'view': True, 'edit': True},
    },
    'RECEPTIONIST': {
        'dashboard': True,
        'patients': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'appointments': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'doctors': {'view': True, 'create': False, 'edit': False, 'delete': False},
        'billing': {'view': True, 'create': True, 'edit': True, 'delete': False},
    },
    'PHARMACIST': {
        'dashboard': True,
        'prescriptions': {'view': True, 'create': False, 'edit': False, 'delete': False},
        'inventory': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'patients': {'view': True, 'create': False, 'edit': False, 'delete': False},
    },
    'ACCOUNTANT': {
        'dashboard': True,
        'billing': {'view': True, 'create': True, 'edit': True, 'delete': True},
        'reports': {'view': True, 'create': True},
        'appointments': {'view': True, 'create': False, 'edit': False, 'delete': False},
        'patients': {'view': True, 'create': False, 'edit': False, 'delete': False},
    },
    'STAFF': {
        'dashboard': True,
        'patients': {'view': True, 'create': True, 'edit': True, 'delete': False},
        'appointments': {'view': True, 'create': True, 'edit': True, 'delete': False},
    }
}


def get_user_menu(user):
    """
    Get menu configuration for a user based on their role
    
    Args:
        user: User instance
        
    Returns:
        dict: Menu configuration with allowed items and actions
    """
    role = user.role.upper()
    menu = ROLE_MENU_CONFIG.get(role, {})
    
    return {
        'role': role,
        'role_display': user.get_role_display(),
        'menu': menu
    }


def can_access_module(user, module_name):
    """
    Check if user can access a specific module
    
    Args:
        user: User instance
        module_name: Name of the module (e.g., 'patients', 'prescriptions')
        
    Returns:
        bool: True if user can access the module
    """
    role = user.role.upper()
    menu = ROLE_MENU_CONFIG.get(role, {})
    return module_name in menu


def can_perform_action(user, module_name, action):
    """
    Check if user can perform a specific action on a module
    
    Args:
        user: User instance
        module_name: Name of the module
        action: Action to check ('view', 'create', 'edit', 'delete')
        
    Returns:
        bool: True if user can perform the action
    """
    role = user.role.upper()
    menu = ROLE_MENU_CONFIG.get(role, {})
    module = menu.get(module_name)
    
    if isinstance(module, dict):
        return module.get(action, False)
    
    # If module is True (not a dict), allow view only
    return module and action == 'view'
