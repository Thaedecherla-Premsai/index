import sqlite3
import string
import random
from flask import Flask, request, redirect, render_template

app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('url_shortener.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS url_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_code TEXT NOT NULL
    )
''')
conn.commit()

def generate_short_code():
    # Generate a random 6-character short code
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']

    # Check if the URL is already in the database
    cursor.execute('SELECT short_code FROM url_mapping WHERE original_url = ?', (original_url,))
    result = cursor.fetchone()

    if result:
        short_code = result[0]
    else:
        # Generate a new short code
        short_code = generate_short_code()

        # Insert into the database
        cursor.execute('INSERT INTO url_mapping (original_url, short_code) VALUES (?, ?)', (original_url, short_code))
        conn.commit()

    short_url = request.host_url + short_code
    return render_template('index.html', short_url=short_url)

@app.route('/<short_code>')
def redirect_to_original(short_code):
    # Retrieve the original URL from the database
    cursor.execute('SELECT original_url FROM url_mapping WHERE short_code = ?', (short_code,))
    result = cursor.fetchone()

    if result:
        original_url = result[0]
        return redirect(original_url)
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True)
