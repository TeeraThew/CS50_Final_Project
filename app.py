# Main source code of the web pplication

import os

# Import the "sqlite3" module
import sqlite3

from sqlalchemy import create_engine, Table, MetaData, text, Integer, String, Sequence

from sqlalchemy.ext.automap import automap_base


# Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy to your application.
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, flash, redirect, render_template, request, session, url_for
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

import ast

# # Global constants
# MAX = {
#     'ACCOUNT_LENGTH': 20,
#     'CATEGORY_LENGTH': 20,
#     'DESCRIPTON-LENGTH': 100,
#     'MONEY': 10**2
# }


# Create an instance of the "Flask" class and pass the Flask constructor the path of the correct module 
#   so that Flask knows where to look for resources such as templates and static files.
app = Flask(__name__)

#  Register our own filters in Jinja
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config["SECRET_KEY"] = "x!\x8d\x8d\x974\xae\xa2\xc6\x05\x89\x00"   
# configure the SQLite database, relative to the app instance folder

# db = SQLAlchemy(app)


# users = db.Table('users', db.metadata, autoload=True, autoload_with=db.engine)

# Base = automap_base()
# Base.prepare(db.engine, reflect=True)
# users = Base.classes.users

Session(app)


# # create the extension
# db = SQLAlchemy()

# # initialize the app with the extension
# db.init_app(app)

# The name of the database file (.db file)
db_name = "database.db"


# db = create_engine('sqlite:///dogscats.db')
# metadata = MetaData(bind=db)
# users = Table('users', metadata, autoload=True)
# cases = Table('cases', metadata, autoload=True)

# # Create a connection to the database "database_name.db" in the current working directory, 
# # implicitly creating it if it does not exist.
# # The returned Connection object con represents the connection to the on-disk database.
# conn = sqlite3.connect('database.db', connect_args={"check_same_thread": False})

# conn = create_engine(
# 'sqlite:///database.db',
# connect_args={'check_same_thread': False}
# )

conn = sqlite3.connect('database.db', check_same_thread=False)

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
account TEXT,
category TEXT,
description TEXT,
income	REAL NOT NULL DEFAULT 0.00,
expense	REAL NOT NULL DEFAULT 0.00,
FOREIGN KEY(user_id) REFERENCES users(id)
)""")
    
    
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
    # Get user's id of current user
    user_id = session["user_id"]

    # If the user have not logged in yet
    if not user_id:
        return render_template("login.html")

    # Get the balance of each account
    try:
        transactions_db = cur.execute(
            "SELECT account, SUM(income) AS total_income, SUM(expense) AS total_expense  FROM transactions WHERE user_id = :user_id GROUP BY account", {'user_id': user_id}
        )
        transactions_db = transactions_db.fetchall()
    except:
        apology("Database error occurred", 500)

    # Add the key "balance" to each dictionary in the list of transactions
    for row in transactions_db:
        row["balance"] = row["total_income"] - row["total_expense"]

    # Total income, total expense, total balance from all accounts
    income_total = 0
    expense_total = 0
    balance_total = 0
    for row in transactions_db:
        income_total += row["total_income"]
        expense_total += row["total_expense"]
        balance_total += row["balance"]
        
    # Find how much cash the user currently has in the table "users"
    try:
        user_cash_db = cur.execute("SELECT cash FROM users WHERE id = :user_id", {'user_id': user_id})
        user_cash_db = user_cash_db.fetchall()
        user_cash = user_cash_db[0]["cash"]
    except:
        return apology("Database error occurred", 500)
    
    # Render homepage
    return render_template(
        "index.html",
        transactions_db=transactions_db,
        income_total=income_total,
        expense_total=expense_total,
        balance_total=balance_total,
        user_cash=user_cash
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Input validation
        is_valid = True
        
        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")
        
        # You can also prevent empty user input on the client-side by adding the "required" attribute to the <input> tag
        # In general, it is best to perform input validation on both the client side and server side. 
        # Client-side input validation can help reduce server load and can prevent malicious users from submitting invalid data. 
        # However, client-side input validation is not a substitute for server-side input validation. Server-side input validation is essential to ensure that only valid data is processed by the application. 
        
        # Ensure username was submitted (This is a server-side validation)
        if not username:
            is_valid = False
            flash("must provide username")

        # Ensure password was submitted
        if not password:
            is_valid = False
            flash("must provide password")
            
        if not is_valid:
            return render_template("login.html")

        # Query database for username
        try:
            rows = cur.execute("SELECT * FROM users WHERE username = :username", {'username': username})
            rows = rows.fetchall()
        except:
            return apology("Database error occurred", 500)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            is_valid = False
            flash("invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Input validation
        is_valid = True
        
        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmed_password = request.form.get("confirmation")
        
        # Ensure username was submitted
        if not username:
            is_valid = False
            flash("Must provide username")
            
        # Ensure password was submitted
        if not password:
            is_valid = False
            flash("Must provide password")
        # Ensure password confirmation was submitted
        elif not confirmed_password:
            is_valid = False
            flash("Must confirm password")
        # Ensure password and confirmed password are matched
        elif password != confirmed_password:
            is_valid = False
            flash("Password and confirmed password are not matched")
            
        # Ensure password is valid
        if not validate_password(password):
            is_valid = False
            flash(
                "Password must contain at least one digit and one special character"
            )
            
        # Ensure the username does not exist in the database
        try:
            rows = cur.execute("SELECT * FROM users WHERE username = :username", {'username': username})
            rows = rows.fetchall()
        except:
            return apology("Database error occurred", 500)
    
        if rows:
            is_valid = False
            flash("Username already exists")
        # Another way:
        # usernames = cur.execute("SELECT username FROM users")
        # usernames = usernames.fetchall()
        # Check if the username already exists within the list "usernames" of dictionaries
        # if any(dict["username"] == username for dict in usernames):
        #   return apology("username already exists", 403)
        
        hash = generate_password_hash(request.form.get("password"))
        # Insert user data into database
        try:
            with conn:
                new_user_cur = cur.execute(
                    "INSERT INTO users (username, hash) VALUES(:username, :hash)", {'username': username, 'hash': hash}
                )
                # Get the row id of the new user after inserted into the table "users"
                new_user_id = new_user_cur.lastrowid
        except:
            is_valid = False
            flash("Cannot insert user data")  
        # Another way is to show an auto-generated error message: 
        # except Exception as e:
        #     return apology(str(e))
        
        if not is_valid:
            return render_template("register.html", username=username)
        else:
            # Remember which user has logged in
            session["user_id"] = new_user_id

            # Render home page
            flash("You have registered!")
            return redirect("/")

    # User reached route via GET (as by clicking a link or entering the URL or via redirect)
    else:
        return render_template("register.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get current user's id
    user_id = session["user_id"]

    # Get user's transactions
    try:
        transactions_db = cur.execute(
            """SELECT * FROM transactions WHERE user_id = :user_id 
            ORDER BY date DESC, id DESC""", 
            {'user_id': user_id}
        )
        transactions_db = transactions_db.fetchall()
    except:
        return apology("Database error occurred", 500)

    # Add the key "balance" to each dictionary in the list of transactions
    for row in transactions_db:
        row["balance"] = row["income"] - row["expense"]

    return render_template("history.html", transactions_db=transactions_db)


@app.route("/add_transactions", methods=["GET", "POST"])
@login_required
def add_transactions():
    """Add transactions"""
    # User reached route via GET
    if request.method == "GET":
        return render_template("add_transactions.html")

    # User reached route via POST
    else:
        # Input validation
        is_valid = True
        
        # Get input data from the form
        date = request.form.get("date")
        account = request.form.get("account")
        category = request.form.get("category")
        description = request.form.get("description")
        
        income = request.form.get("income")
        if not income:
            income = 0
        income = float(income)
        
        expense = request.form.get("expense")
        if not expense:
            expense = 0
        expense = float(expense)
        
        # If the input is blank
        if not account:
            is_valid = False
            flash("Must provide account")

        # If shares is not a positive integer
        if income < 0 or expense < 0:
            is_valid = False
            flash("Income and expense must be nonnegative")
            
        # If both income and expense are 0
        if income == 0 and expense == 0:
            is_valid = False
            flash("Either income or expense must be positive")
        
        if not is_valid:
            return render_template(
                "add_transactions.html",
                date=date,
                account=account,
                category=category,
                description=description,
                income=income, 
                expense=expense
                )

        # Get user's id of current user
        user_id = session["user_id"]
        
        # # Get current date and time
        # date = current_time()

        # Insert new transaction into transaction history (in table "transactions")
        try:
            with conn:
                cur.execute(
                    """INSERT INTO transactions (user_id, date, account, category, description, income, expense) 
                    VALUES (:user_id, :date, :account, :category, :description, :income, :expense)""",
                    {'user_id': user_id,
                    'date': date,
                    'account': account,
                    'category': category,
                    'description': description,
                    'income': income,
                    'expense': expense}
                )
        except:
            return apology("Database error occurred", 500)

        # Redirect user to home page
        flash("Transactions added!")
        return redirect(url_for("index"))
    

@app.route("/editing_transaction", methods=["POST"])
@login_required
def editing_transaction():
    """Editing transaction"""
    if request.method == "POST":
        # Get the transaction row as a string (i.e. it is the string representation of the dictionary)
        # So we need to convert the string to the original dictionary first.
        transaction_row = request.form.get("transaction_to_edit")
        # Convert the string representation to the dictionary
        transaction_row = ast.literal_eval(transaction_row)
        
        # print(f"transaction_row = {transaction_row}")
        # print(f"transaction_row[0] = {transaction_row[0]}")
        # print("income = " + income)
        return render_template(
            "editing_transaction.html", 
            transaction_id=transaction_row['id'],
            date=transaction_row['date'],
            account=transaction_row['account'],
            category=transaction_row['category'],
            description=transaction_row['description'],
            income=transaction_row['income'],
            expense=transaction_row['expense']
            )
    else:
        return apology("An error occurred", 500)
        


@app.route("/edit_transactions", methods=["GET", "POST"])
@login_required
def edit_transactions():
    """Edit transactions"""
    
    # User reached route via GET
    if request.method == "GET":
        # Get current user's id
        user_id = session["user_id"]

        # Get user's transactions
        try:
            transactions_db = cur.execute(
                """SELECT * FROM transactions WHERE user_id = :user_id
                ORDER BY date DESC, id DESC""", 
                {'user_id': user_id}
            )
            transactions_db = transactions_db.fetchall()
        except:
            return apology("Database error occurred", 500)

        # Add the key "balance" to each dictionary in the list of transactions
        for row in transactions_db:
            row["balance"] = row["income"] - row["expense"]

        return render_template("edit_transactions.html", transactions_db=transactions_db)
    
    elif request.method == "POST":
        # Get user's id of current user
        user_id = session["user_id"]
        
        # Get the id of the transaction that is to be edited
        transaction_id = request.form.get("transaction_to_edit_id") 

        # Input validation
        is_valid = True
        
        # Get input data from the form
        date = request.form.get("date")
        account = request.form.get("account")
        category = request.form.get("category")
        description = request.form.get("description")
        
        income = request.form.get("income")
        if not income:
            income = 0
        income = float(income)
        
        expense = request.form.get("expense")
        if not expense:
            expense = 0
        expense = float(expense)
        
        # If the input is blank
        if not account:
            is_valid = False
            flash("Must provide account")

        # If shares is not a positive integer
        if income < 0 or expense < 0:
            is_valid = False
            flash("Income and expense must be nonnegative")
            
        # If both income and expense are 0
        if income == 0 and expense == 0:
            is_valid = False
            flash("Either income or expense must be positive")
            
        if not is_valid:
            return render_template(
                "editing_transaction.html", 
                date=date,
                account=account,
                category=category,
                description=description,
                income=income, 
                expense=expense
                )

        # Update the transaction (in table "transactions")
        try:
            with conn:
                cur.execute(
                    """UPDATE transactions 
                        SET date = :date, 
                            account = :account, 
                            category = :category, 
                            description = :description, 
                            income = :income, 
                            expense = :expense
                        WHERE user_id = :user_id 
                        AND id = :transaction_id
                    """,
                    {'user_id': user_id,
                    'transaction_id': transaction_id,
                    'date': date,
                    'account': account,
                    'category': category,
                    'description': description,
                    'income': income,
                    'expense': expense
                    }) 
        except:
            return apology("Database error occurred", 500)
        
        # Redirect user to edit_transactions page
        flash("Transactions edited!")
        return redirect(url_for("edit_transactions"))
        
    else:
        return apology("An error occurred", 500)


@app.route("/delete_transaction", methods=["POST"])
@login_required
def delete_transaction():
    """Delete transaction"""
    if request.method == "POST":
        # Get user's id of current user
        user_id = session["user_id"]
        
        # Get the id of the transaction that is to be deleted
        transaction_id = request.form.get("transaction_to_delete_id") 

        # Delete the transaction (in table "transactions")
        try:
            with conn:
                cur.execute(
                    """DELETE FROM transactions 
                        WHERE user_id = :user_id 
                        AND id = :transaction_id
                    """,
                    {'user_id': user_id,
                    'transaction_id': transaction_id
                    }) 
        except:
            return apology("Database error occurred", 500)
        
        # Redirect user to edit_transactions page
        flash("Transactions deleted!")
        return redirect(url_for("edit_transactions"))
        
    else:
        return apology("An error occurred", 500)

if __name__ == "__main__":
    #  Run the flask application with debug mode as "ON"
    app.run(debug = True)

