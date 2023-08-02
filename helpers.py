# Snippets, defined functions

import re
from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """ Escape special characters: https://github.com/jacebrowning/memegen#special-characters"""
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", message=message, top=code, bottom=escape(message)), code


def login_required(f):
    """Decorate routes to require login: https://flask.palletsprojects.com/en/2.3.x/views/#view-decorators"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
    # return value


def validate_password(password):
    """Validate password: return True if password is valid, else False"""
    # Define a regex pattern for validation
    # Require passwords to have at least one digit (0-9) and one special character (#, ?, !, @, $, %, ^, &, *, -, _)
    reg = r"^(?=.*?[0-9])(?=.*?[#?!@$%^&*-_])"
    pattern = re.compile(reg)
    return re.match(pattern, password)
