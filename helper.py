from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
        Decorate routes to require login.

        http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
        """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/teacher")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
        Decorate routes to require login.

        http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
        """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect("/teacher")
        return f(*args, **kwargs)

    return decorated_function


def teacher_required(f):
    """
        Decorate routes to require login.

        http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
        """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("teacher_id") is None:
            return redirect("/teacher")
        return f(*args, **kwargs)

    return decorated_function


def cash_required(f):
    """
        Decorate routes to require login.

        http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
        """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("cash_id") is None:
            return redirect("/teacher")
        return f(*args, **kwargs)

    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("error.html", message=escape(message), code=code), code