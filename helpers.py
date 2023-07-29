import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import re

from flask import redirect, render_template, session
from functools import wraps


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
    return render_template("apology.html", message=message, top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


# Check if password is valid
def validate_password(password):
    """Validate password: return True if password is valid, else False"""
    # Define a regex pattern for validation
    # Require passwords to have at least one digit and one special character
    reg = r"^(?=.*?[0-9])(?=.*?[#?!@$%^&*-])"
    pattern = re.compile(reg)
    return re.match(pattern, password)


# Return current date and time
def current_time():
    return datetime.datetime.now(pytz.timezone("Asia/Bangkok")).replace(microsecond=0, tzinfo=None)