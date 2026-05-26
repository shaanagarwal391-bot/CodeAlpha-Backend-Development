# -CodeAlpha-Backend-Development-Task-1-Simple-URL-shortener
# CodeAlpha Backend Development - Task 1: Simple URL Shortener  An elegant, full-stack URL Shortener platform featuring a robust REST API built with Python (Flask) and SQLite, paired with a sleek, interactive user interface built with Streamlit.
# CodeAlpha_Simple_URL_Shortener

A full-stack, lightweight URL Shortener built as part of the CodeAlpha Backend Development Internship (Task 1). This project features a robust RESTful API backend handling URL redirection and database mapping, paired with a modern, responsive user interface.

## 🚀 Features
* **URL Shortening:** Converts long, cumbersome HTTP/HTTPS links into compact, unique 6-character short codes.
* **Redirection Engine:** Automatically decodes valid short codes and routes users instantly to their original destination.
* **Persistent Storage:** Prevents duplicate entries and maps link pairs securely using SQLite.
* **Modern UI:** Built a highly polished, dark-themed frontend using Streamlit for an intuitive user experience.

---

## 🛠️ Tech Stack
* **Backend Framework:** Flask (Python)
* **Frontend Interface:** Streamlit (Custom Dark CSS)
* **Database Engine:** SQLite3 (Embedded)
* **Communication Layer:** REST API (JSON payloads via `requests`)

---

## 📂 Project Structure
```text
CodeAlpha_ProjectName/
│
├── app.py               # Flask REST API Backend & Database logic
├── frontend.py          # Streamlit UI dashboard
├── database.db          # SQLite relational database (Auto-generated)
└── README.md            # Project documentation
