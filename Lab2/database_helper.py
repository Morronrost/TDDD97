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

    db.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receiver_email TEXT NOT NULL,
        sender_email TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)
    db.commit()



def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
        db.row_factory = sqlite3.Row
    return db


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

def sign_out(token):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT email FROM users WHERE token=?", (token,)).fetchone()

    if not user:
        return False

    cursor.execute("UPDATE users SET token=NULL WHERE token=?", (token,))

    db.commit()
    db.close()
    return True


def change_password(token, oldpassword, newpassword):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT password, token FROM users WHERE token=?", (token,)).fetchone()
    
    if not user:
        return False, "token"
    elif user["token"] != token:
        return False, "token"
    elif user["password"] != oldpassword:
        return False, "password"
    else:
        cursor.execute("UPDATE users SET password=? WHERE token=?", (newpassword, token,))
        return True, None

def get_user_data_by_token(token):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT email, firstname, familyname, gender, city, country FROM users WHERE token=?", (token,)).fetchone()
    if not user:
        return False, None

    return True, user

def get_user_data_by_email(token, email):
    db = get_db()
    cursor = db.cursor()

    user = cursor.execute("SELECT email, firstname, familyname, gender, city, country FROM users WHERE email=?", (email,)).fetchone()

    if not user:
        return False, None
    
    return True, user

def get_user_messages_by_email(email):
    db = get_db()
    cursor = db.cursor()

    rows = cursor.execute("SELECT sender_email, content FROM messages WHERE receiver_email=?", (email,)).fetchall()

    messages = [dict(row) for row in rows]

    return True, messages

def post_message(token, message, email):
    db = get_db()
    cursor = db.cursor()

    data = get_user_data_by_token(token)[1]

    cursor.execute("INSERT INTO messages (receiver_email, sender_email, content) VALUES (?, ?, ?)", (email, data["email"], message))
    db.commit()
    db.close()
    return True

