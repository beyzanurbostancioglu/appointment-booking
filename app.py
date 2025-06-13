from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
