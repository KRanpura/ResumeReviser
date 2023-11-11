from flask import redirect, render_template, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs): # if you put @login in app.py, it'll first check if user logged in
        if session.get("user_id") is None:   # before going to the new page like upload resume page
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function