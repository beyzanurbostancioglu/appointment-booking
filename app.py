from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db_connection():
    conn = sqlite3.connect('appointments.db')
    conn.row_factory = sqlite3.Row
    return conn

# Anasayfa - Randevu formu
@app.route('/')
def index():
    return render_template('index.html')

# Randevu kaydetme
@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    time = request.form['time']

    conn = get_db_connection()
    conn.execute('INSERT INTO appointments (name, email, date, time) VALUES (?, ?, ?, ?)',
                 (name, email, date, time))
    conn.commit()
    conn.close()

    return redirect('/success')

# Başarı sayfası
@app.route('/success')
def success():
    return render_template('success.html')

# Admin paneli - randevuları listele
@app.route('/admin')
def admin():
    conn = get_db_connection()
    appointments = conn.execute('SELECT * FROM appointments').fetchall()
    conn.close()
    return render_template('admin.html', appointments=appointments)

if __name__ == '__main__':
    # Tablonun varlığını kontrol et, yoksa oluştur
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
