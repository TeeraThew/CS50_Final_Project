

import os

# Import the "sqlite3" module
import sqlite3

from sqlalchemy import create_engine, Table, MetaData, text, Integer, String, Sequence
from sqlalchemy.future.orm import Session as sql_Session

# Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy to your application.
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    apology,
    login_required,
    usd,
    current_time,
    validate_password
)

# Create a connection to the database "database_name.db" in the current working directory, 
# implicitly creating it if it does not exist.
# The returned Connection object con represents the connection to the on-disk database.
conn = sqlite3.connect('database.db')

# # Alternatively, we can create an SQLite database existing only in memory (RAM), and open a connection to it,
# # Note that, in this case, the database will only exist temporarily and will be refreshed every time you run the program
# # It is useful when you want to fresh-clean database on every run, so that you don't have to delete data in database over and over
# conn = sqlite3.connect(':memory:')

# Create a custom row_factory that returns each row as a dict, with column names mapped to values.
# Using it, queries will return a dict instead of a tuple.
# After you execute a query, the result will be a cursor object, so you have to fetch the result first (by using fetch.all(), fetchone(), fetchmany())
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}
conn.row_factory = dict_factory

# In order to execute SQL statements and fetch results from SQL queries, we need to use a database cursor. 
# Call con.cursor() to create the Cursor
cur = conn.cursor()

def main():
    # Create a database table named "users"
    # Execute the CREATE TABLE statement by calling cur.execute(...)
    # Used only when we want to create a table for the first time
    # Use the "IF NOT EXISTS" clause to avoid an error when a table with the same name already exists
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL, 
    hash TEXT NOT NULL, 
    cash NUMERIC NOT NULL DEFAULT 0.00
    )""")
    
    # Creates an index named "username" on the "username" column in the "users" table
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)")
    
    # Create a table named "transactions"
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    user_id INTEGER,
    date DATE,
    account	TEXT,
    category TEXT,
    description TEXT,
    income	REAL NOT NULL DEFAULT 0.00,
    expense	REAL NOT NULL DEFAULT 0.00,
    FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    
# Create an instance of the "Flask" class and pass the Flask constructor the path of the correct module 
#   so that Flask knows where to look for resources such as templates and static files.
app = Flask(__name__)

#  Register our own filters in Jinja
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# app.config["SECRET_KEY"] = "x!\x8d\x8d\x974\xae\xa2\xc6\x05\x89\x00"   
# configure the SQLite database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"

Session(app)

# # create the extension
# db = SQLAlchemy()

# # initialize the app with the extension
# db.init_app(app)

# The name of the database file (.db file)
db_name = "database.db"


# Ensure responses after each request aren't cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        username = request.form.get("username")
        rows = cur.execute("SELECT * FROM users WHERE username = :username", {'username': username})
        rows = rows.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmed_password = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        if not password:
            return apology("must provide password")

        # Ensure password confirmation was submitted
        if not confirmed_password:
            return apology("must confirm password")

        # Ensure password and confirmed password are matched
        if password != confirmed_password:
            return apology("password and confirmed password are not matched")

        # Ensure password is valid
        if not validate_password(password):
            return apology(
                "password must have at least one digit and one special character"
            )

        # Ensure the registered username have not existed before
        # # Query database for username
        rows = cur.execute("SELECT * FROM users WHERE username = :username", {'username': username})
        rows = rows.fetchall()
        if rows:
            return apology("username already exists")

        # Another way:
        # usernames = db.execute("SELECT username FROM users")
        # Check if the username already exists within the list "usernames" of dictionaries
        # if any(dict["username"] == username for dict in usernames):
        #   return apology("username already exists", 403)

        hash = generate_password_hash(request.form.get("password"))
        # Insert user's data into database
        try:
            new_user = cur.execute(
                "INSERT INTO users (username, hash) VALUES(:username, :hash)", {'username': username, 'hash': hash}
            )
            new_user = new_user.fetchall()
            
        except:
            return apology("username already exists")

        # Remember which user has logged in
        session["user_id"] = new_user

        # Render home page
        flash("You have registered!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


if __name__ == "__main__":
    #  Run the flask application with debug mode as "ON"
    app.run(debug = True)

