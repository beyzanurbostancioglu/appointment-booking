from flask import Flask, render_template, request, redirect, flash, session
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8!'

def get_db_connection():
    conn = sqlite3.connect('appointments.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    time = request.form['time']

    # E-posta doğrulama
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        flash('Please enter a valid email address.')
        return redirect('/')

    try:
        t = datetime.strptime(time, '%H:%M')
    except ValueError:
        flash('Invalid time format.')
        return redirect('/')

    if t.minute not in [0, 30]:
        flash('Please select a time in 30-minute intervals.')
        return redirect('/')

    if t.hour < 9 or t.hour > 18 or (t.hour == 18 and t.minute > 0):
        flash('Please select a time between 09:00 and 18:00.')
        return redirect('/')

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT * FROM appointments WHERE date = ? AND time = ?',
        (date, time)
    ).fetchone()

    if existing:
        conn.close()
        flash('This time slot is already booked. Please choose another time.')
        return redirect('/')

    conn.execute(
        'INSERT INTO appointments (name, email, date, time) VALUES (?, ?, ?, ?)',
        (name, email, date, time)
    )
    conn.commit()
    conn.close()

    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success.html')

# ---------- ADMIN LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password123':
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            flash('Invalid username or password')
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.')
    return redirect('/login')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    conn = get_db_connection()
    appointments = conn.execute('SELECT * FROM appointments').fetchall()
    conn.close()
    return render_template('admin.html', appointments=appointments)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('admin_logged_in'):
        return redirect('/login')
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Appointment deleted successfully.')
    return redirect('/admin')

if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    app.run(debug=True)
