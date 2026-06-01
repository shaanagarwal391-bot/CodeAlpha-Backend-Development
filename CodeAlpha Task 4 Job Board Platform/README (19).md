# 💼 Job Board Platform

A full-stack **Job Board Platform** developed as **Task 4** for the **CodeAlpha Backend Development Internship**. This project allows employers to post jobs, candidates to create profiles and apply for jobs, and employers to manage application statuses. It includes a **Flask REST API backend**, **SQLite database**, and a **Streamlit frontend dashboard**.

---

## 🚀 Features

### 👨‍💼 Employer Features
- Post new job listings
- Manage job applications
- Update application statuses
- Receive simulated application notifications

### 👨‍💻 Candidate Features
- Create and update candidate profiles
- Upload resume information
- Search jobs by keyword and location
- Apply for available jobs
- Track application status

### 🔍 Job Search Features
- Search jobs by title or description
- Filter jobs by location
- View detailed job information

---

## 🛠️ Technology Stack

### Backend
- Python
- Flask
- SQLite3
- REST API

### Frontend
- Streamlit

### Database
- SQLite

---

## 📂 Project Structure

```text
JobBoardPlatform/
│
├── requirements.txt       
├── job_board.db            # SQLite Database (auto-generated)
├── frontend.py             # Streamlit Frontend Dashboard
├── app.py                  # Flask Backend API
└── README.md
```

---

## 🗄️ Database Schema

### Employers

| Field | Type |
|---------|---------|
| id | INTEGER |
| company_name | TEXT |
| website | TEXT |
| description | TEXT |

### Job Listings

| Field | Type |
|---------|---------|
| id | INTEGER |
| employer_id | INTEGER |
| title | TEXT |
| description | TEXT |
| location | TEXT |
| job_type | TEXT |
| salary_range | TEXT |

### Candidates

| Field | Type |
|---------|---------|
| id | INTEGER |
| username | TEXT |
| skills | TEXT |
| resume_text | TEXT |

### Applications

| Field | Type |
|---------|---------|
| id | INTEGER |
| job_id | INTEGER |
| candidate_id | INTEGER |
| cover_letter | TEXT |
| status | TEXT |

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/CodeAlpha_JobBoardPlatform.git
cd CodeAlpha_JobBoardPlatform
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install flask streamlit requests
```

---

## ▶️ Running the Application

### Start Flask Backend

```bash
python app.py
```

Backend runs on:

```text
http://127.0.0.1:5000
```

### Start Streamlit Frontend

Open another terminal:

```bash
streamlit run frontend.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

## 📡 API Endpoints

### 1. Get All Jobs

```http
GET /api/jobs
```

### Search Jobs

```http
GET /api/jobs?search=python&location=remote
```

---

### 2. Post a Job

```http
POST /api/jobs
```

Request Body:

```json
{
  "employer_id": 1,
  "title": "Python Developer",
  "description": "Backend development role",
  "location": "Remote",
  "job_type": "Full-Time",
  "salary_range": "$50,000 - $70,000"
}
```

---

### 3. Create/Update Candidate Profile

```http
POST /api/candidates
```

```json
{
  "username": "john_doe",
  "skills": "Python, Flask",
  "resume_text": "Experienced Backend Developer"
}
```

---

### 4. Apply for a Job

```http
POST /api/applications
```

```json
{
  "job_id": 1,
  "candidate_id": 1,
  "cover_letter": "I am interested in this position."
}
```

---

### 5. Track Applications

```http
GET /api/applications?candidate_id=1
```

---

### 6. Update Application Status

```http
PATCH /api/applications/<app_id>/status
```

```json
{
  "status": "ACCEPTED"
}
```

Valid Status Values:

```text
PENDING
REVIEWING
ACCEPTED
REJECTED
```

---

## 🎯 Task Requirements Covered

The project successfully implements:

✅ Job Listings Management

✅ Employer Management

✅ Candidate Profiles

✅ Resume Handling

✅ Job Search Filters

✅ Job Applications

✅ Application Tracking

✅ Status Updates

✅ Employer Notifications (Simulated)

✅ SQLite Database Integration

✅ REST API Architecture

✅ Frontend Dashboard using Streamlit

---

## 📸 Future Enhancements

- JWT Authentication
- File-based Resume Uploads (PDF/DOCX)
- Email Notifications
- Admin Dashboard
- Application Analytics
- Employer Verification
- Cloud Database Support (PostgreSQL/MySQL)
- Docker Deployment

---

## 👨‍💻 Author

**CodeAlpha Backend Development Internship — Task 4**

Project: **Job Board Platform**

Built using Flask, SQLite, and Streamlit.

---

## 📄 License

This project is created for educational and internship evaluation purposes under the CodeAlpha Backend Development Internship Program.
