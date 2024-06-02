from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'asDASd'

# Создаем базу данных и таблицу для учетных записей сотрудников
def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                isAdmin BOOLEAN
              )''')
    conn.commit()
    conn.close()

    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests 
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT, request TEXT, status TEXT)''')
    conn.commit()
    conn.close()

# Функция для добавления учетной записи сотрудника в базу данных
def add_user(username, password, isAdmin):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, isAdmin) VALUES (?, ?, ?)", (username, password, isAdmin))
    conn.commit()
    conn.close()

def add_master():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, isAdmin) VALUES (?, ?, ?)", ("Ivanov", "i1", True))
    conn.commit()
    conn.close()

# Получаем все учетные записи сотрудников из базы данных
def get_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users

# Функция для получения всех запросов из базы данных
def get_all_requests():
    conn = sqlite3.connect("requests.db")
    c = conn.cursor()
    c.execute('SELECT * FROM requests WHERE name = ?', (session["username"],))
    requests = c.fetchall()
    conn.close()
    return requests

# Основная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = session['username']
        requests = get_all_requests()

        return render_template('main.html', username=username, requests=requests)
    return redirect(url_for('login'))

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if check_credentials(username, password):
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html')

# Функция для проверки учетных данных
def check_credentials(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    employee = c.fetchone()
    conn.close()
    return employee is not None

# Функция регистрации пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            isAdmin = False
            add_user(username, password, isAdmin)
            return redirect(url_for('login'))
    return render_template('register.html')

# Выход из учетной записи
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Форма добавления записи в БД requests
@app.route('/add', methods=['GET', 'POST'])
def add_request():
    if request.method == 'POST':
        email = request.form['email']
        req = request.form['request']
        status = 'New'

        conn = sqlite3.connect("requests.db")
        c = conn.cursor()
        c.execute("INSERT INTO requests (name, email, request, status) VALUES (?, ?, ?, ?)",
                  (session["username"], email, req, status))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_request.html', username=session["username"])

if __name__ == '__main__':
    create_database()
    app.run(debug=True)