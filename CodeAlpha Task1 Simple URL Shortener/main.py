# Task 1
import string
import random
import sqlite3
from flask import Flask, request, redirect, jsonify, abort

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
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
    return jsonify({"status": "Backend running successfully"}), 200

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'long_url' not in data:
        return jsonify({"error": "Missing 'long_url' parameter"}), 400
    
    long_url = data['long_url'].strip()
    if not long_url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL format. Must start with http:// or https://"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT short_code FROM urls WHERE long_url = ?", (long_url,))
        row = cursor.fetchone()
        
        if row:
            short_code = row[0]
        else:
            short_code = generate_short_code()
            cursor.execute("INSERT INTO urls (long_url, short_code) VALUES (?, ?)", (long_url, short_code))
            conn.commit()

    short_url = f"{request.host_url}{short_code}"
    return jsonify({"short_url": short_url, "short_code": short_code}), 200

@app.route('/<short_code>')
def redirect_to_url(short_code):
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

import streamlit as st
import requests

st.set_page_config(
    page_title="URL Shortener | CodeAlpha",
    page_icon="🔗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styles
st.markdown(
    """
    <style>
        .stApp { background-color: #0f172a; color: #f8fafc; }
        div[data-testid="stForm"] {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center; font-size: 2.25rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>URL Shortener</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.875rem; margin-bottom: 2rem;'>CodeAlpha Backend Task 1</p>", unsafe_allow_html=True)

# Function interacting with the TRUE backend
def call_backend_api(long_url):
    backend_url = "http://127.0.0.1:5000/shorten"
    response = requests.post(backend_url, json={"long_url": long_url})
    if response.status_code == 200:
        return response.json()["short_url"]
    else:
        raise Exception(response.json().get("error", "Failed to shorten"))

with st.form("shorten_form", clear_on_submit=False):
    long_url = st.text_input("Enter Long URL", placeholder="https://example.com")
    submit_btn = st.form_submit_button("Shorten URL", use_container_width=True)

if submit_btn:
    if not long_url.startswith(("http://", "https://")):
        st.error("Please enter a valid URL starting with http:// or https://")
    else:
        try:
            shortened_url = call_backend_api(long_url)
            st.markdown("<p style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #94a3b8; margin-top: 1.5rem;'>Your Shortened URL:</p>", unsafe_allow_html=True)
            st.code(shortened_url, language="text")
            st.success("URL successfully shortened!")
        except Exception as e:
            st.error(f"Error: {e}")
