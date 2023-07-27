
import os

# Import the "sqlite3" module
import sqlite3

# # Create a connection to the database "database_name.db" in the current working directory, 
# # implicitly creating it if it does not exist.
# # The returned Connection object con represents the connection to the on-disk database.
# conn = sqlite3.connect('employee.db')
# Alternatively, we can create an SQLite database existing only in memory (RAM), and open a connection to it,
# Note that, in this case, the database will only exist temporarily and will be refreshed every time you run the program
# It is useful when you want to fresh-clean database on every run, so that you don't have to delete data in database over and over
conn = sqlite3.connect(':memory:')

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
