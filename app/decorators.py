'''
decorators.py
'''

from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(func):
    ''' admin_required decorator to passed func argument '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        ''' returns func if user is admin'''
        if not current_user.is_administrator():
            abort(403)
        return func(*args, **kwargs)
    return decorated_function

