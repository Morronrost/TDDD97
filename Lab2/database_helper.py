import sqlite3
from flask import g
import random

DATABASE_URI="database.db"

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        firstname TEXT NOT NULL,
        familyname TEXT NOT NULL,
        gender TEXT NOT NULL,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        token TEXT
    )
    """)
    db.commit()

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
        db.row_factory = sqlite3.Row
    return db

def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT email, password FROM users WHERE email=?", (email,)).fetchone()

    return user




def sign_up(email, password, firstname, familyname, gender, city, country):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("INSERT INTO users (email, password, firstname, familyname, gender, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)", (email, password, firstname, familyname, gender, city, country))
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        db.close()
        return False


def sign_in(email, password):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT email, password FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        return False, None

    if not (user["password"] == password):
        return False, None

    letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    token = ""

    for i in range(0,36):
        token += random.choice(letters)
    
    cursor.execute("UPDATE users SET token=? WHERE email=?", (token, email,))
    db.commit()
    db.close()
    
    return True, token


def change_password(token, oldpassword, newpassword):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT password, token FROM users WHERE token=?", (token,)).fetchone()

    if user["token"] != token:
        return False, "token"
    elif user["password"] != oldpassword:
        return False, "password"
    else:
        cursor.execute("UPDATE users SET password=? WHERE token=?", (newpassword, token,))
        return True, None

