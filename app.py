from flask import Flask, render_template, request, redirect, flash
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
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, email):
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
    conn = get_db_connection()
    conn.execute('INSERT INTO appointments (name, email, date, time) VALUES (?, ?, ?, ?)',
                 (name, email, date, time))
    conn.commit()
    conn.close()

    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    appointments = conn.execute('SELECT * FROM appointments').fetchall()
    conn.close()
    return render_template('admin.html', appointments=appointments)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
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
