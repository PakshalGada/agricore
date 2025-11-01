from flask import Flask, request, make_response, redirect
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "users.db"

# Initialize database
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                username TEXT PRIMARY KEY,
                email TEXT,
                password TEXT
            )
        ''')
        conn.commit()
        conn.close()

init_db()

INDEX_HTML = open("template/index.html").read()
LOGIN_HTML = open("template/login.html").read()
REGISTER_HTML = open("template/register.html").read()
STYLE_CSS = open("static/style.css").read()
DASHBOARD_HTML=open("template/dashboard.html").read()
DASHBOARD_CSS=open("static/dashboardStyle.css").read()

def render(html, message="", msg_type=""):
    msg = f'<p class="message {msg_type}">{message}</p>' if message else ""
    return html.replace("<!-- MESSAGE -->", msg)

@app.route('/')
def index():
    return render(INDEX_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()

        if row and check_password(row[0], password):
            return render(DASHBOARD_HTML, f"Welcome back, {username}!", "success")
        else:
            return render(LOGIN_HTML, "Invalid username or password.", "error")
    return render(LOGIN_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(password) < 4:
            return render(REGISTER_HTML, "Password too short (min 4 chars).", "error")

        hashed = generate_password_hash(password)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed))
            conn.commit()
            conn.close()
            return render(LOGIN_HTML, "Registered! Please log in.", "success")
        except sqlite3.IntegrityError:
            conn.close()
            return render(REGISTER_HTML, "Username already exists.", "error")
    return render(REGISTER_HTML)

@app.route('/static/style.css')
def css():
    response = make_response(STYLE_CSS)
    response.headers['Content-Type'] = 'text/css'
    return response
    
@app.route('/static/dashboardStyle.css')
def dashboardCSS():
    response = make_response(DASHBOARD_CSS)
    response.headers['Content-Type'] = 'text/css'
    return response

import hashlib
def generate_password_hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def check_password(stored, provided):
    return hashlib.sha256(provided.encode()).hexdigest() == stored

if __name__ == '__main__':
    app.run(debug=True)
