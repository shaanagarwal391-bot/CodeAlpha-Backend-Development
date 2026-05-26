import string
import random
import sqlite3
from flask import Flask, request, redirect, jsonify, abort

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    """Initializes the SQLite database and creates the urls table if it doesn't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()

def generate_short_code(length=6):
    """Generates a unique 6-character short code containing letters and digits."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,))
            if not cursor.fetchone():
                return code

@app.route('/')
def health_check():
    """Simple API health check endpoint."""
    return jsonify({"status": "Backend running successfully"}), 200

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """
    API Endpoint to accept a long URL, generate a unique short code,
    and save the mapping inside the database.
    """
    data = request.get_json()
    if not data or 'long_url' not in data:
        return jsonify({"error": "Missing 'long_url' parameter"}), 400
    
    long_url = data['long_url'].strip()
    if not long_url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL format. Must start with http:// or https://"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Check if the long URL has already been shortened before
        cursor.execute("SELECT short_code FROM urls WHERE long_url = ?", (long_url,))
        row = cursor.fetchone()
        
        if row:
            short_code = row[0]
        else:
            # Generate a new code and save it
            short_code = generate_short_code()
            cursor.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
            conn.commit()

    short_url = f"{request.host_url}{short_code}"
    return jsonify({"short_url": short_url, "short_code": short_code}), 200

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """
    Redirect route that accepts a short code, looks up the database,
    and forwards the user to the original long URL.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
        row = cursor.fetchone()
        
    if row:
        return redirect(row[0])
    else:
        abort(404, description="Short URL not found")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
