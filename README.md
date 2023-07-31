
# SimpleMoney

**This is my final project for the course [CS50x Introduction to Computer Science](https://cs50.harvard.edu/x/2023) (By David J. Malan) in 2023.** 

## Overview
- This project is web application named "SimpleMoney".
- It is written using HTML, CSS, JavaScript, Python, SQLite, and Flask  
- The main feature of this application is to track users' incomes and expenses.

## Requirements
- [Flask](https://flask.palletsprojects.com)
  - Flask is a micro-framework written in Python for web application development. 
- [SQLite](https://www.sqlite.org)
  - SQLite is a library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

## Database
- All data on users and transactions are stored in the database file "database.db"
- Data are managed by using SQLite3.
- The database contains 2 main tables described by the following schema:
  1. CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      username TEXT NOT NULL,
      hash TEXT NOT NULL);
     CREATE UNIQUE INDEX username ON users (username);
  2. CREATE TABLE transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      user_id INTEGER,
      date DATE,
      account     TEXT,
      category TEXT,
      description TEXT,
      income      REAL NOT NULL DEFAULT 0.00,
      expense     REAL NOT NULL DEFAULT 0.00,
      FOREIGN KEY(user_id) REFERENCES users(id)
      );
  3. CREATE TABLE sqlite_sequence(name,seq);
- The table "sqlite_sequence" is automatically created to store information about autoincrement column.


## Storing transactions.

## Pictures

## Demonstration on youtube
I made a short video to present my final project:
???


## References, documentation, and some useful resources
- CS50's Introduction to Computer Science (Taught by David J. Malan)
    https://www.harvardonline.harvard.edu/course/cs50-introduction-computer-science
- GitHub
    https://github.com
- Bootstrap
    https://getbootstrap.com
- Flask
    https://flask.palletsprojects.com
- SQLite Documentation
    https://www.sqlite.org/docs.html
- W3Schools 
    https://www.w3schools.com
- Python SQLite Tutorial: Complete Overview - Creating a Database, Table, and Running Queries 
    https://www.youtube.com/watch?v=pd-0G0MigUA
- SQLite Databases With Python - Full Course 
    https://www.youtube.com/watch?v=byHcYRpMgI4







