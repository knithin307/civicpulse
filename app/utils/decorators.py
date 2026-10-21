from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict route access to specific roles.
    Example:
        @role_required('admin')
        @role_required('officer', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please sign in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role not in roles:
                flash('You do not have permission to view or perform actions on this page.', 'danger')
                return abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def citizen_required(f):
    return role_required('citizen', 'admin')(f)

def officer_required(f):
    return role_required('officer', 'admin')(f)

def admin_required(f):
    return role_required('admin')(f)
