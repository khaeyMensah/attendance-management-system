from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(roles):
    """Decorator to require a user role (or roles).

    Usage:
        @role_required('student')
        @role_required(('lecturer','admin'))
    """
    if isinstance(roles, str):
        allowed = (roles,)
    else:
        allowed = tuple(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login')
            if getattr(request.user, 'role', None) not in allowed:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
