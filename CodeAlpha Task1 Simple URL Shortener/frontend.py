import streamlit as st
import requests

st.set_page_config(
    page_title="URL Shortener | CodeAlpha",
    page_icon="🔗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Styles for Dark Theme
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

def call_backend_api(long_url):
    """Sends a POST request to the local Flask backend API to shorten the URL."""
    backend_url = "http://127.0.0.1:5000/shorten"
    response = requests.post(backend_url, json={"long_url": long_url})
    if response.status_code == 200:
        return response.json()["short_url"]
    else:
        raise Exception(response.json().get("error", "Failed to shorten"))

# Interactive URL input form
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
