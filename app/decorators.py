from functools import wraps

from app.models import User
from app.utils import send_error


def admin_required():
    """
    Check admin user
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_user = User.get_current_user()
            if not current_user.is_active:
                return send_error(message='You do not have permission')
            return func(*args, **kwargs)

        return inner

    return wrapper
