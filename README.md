# Restaurant Management System Backend

A robust, lightweight RESTful API built with Flask and Flask-SQLAlchemy to handle restaurant operations efficiently. This project fulfills **TASK 3: Restaurant Management System** for the CodeAlpha Backend Development Internship.

The system manages dynamic digital operations including menu tracking, real-time table availability updates, guest capacity-validated reservations, transactional order processing, automated atomic stock deductions, and administrative table configuration updates.

---

## 🚀 Features

* **Menu Management:** Fetch and view available menu items along with their prices.
* **Table Availability:** Check real-time table availability states instantly.
* **Capacity-Validated Reservations:** Book reservations safely with checks against maximum guest limits and table occupancy status.
* **Atomic Order Processing:** Place multi-item orders with transactional inventory verification. If one item is out of stock, the entire order cleanly fails without leaving partial inventory deductions (Session Safety).
* **Live Stock Controls:** Track ingredients and pre-assembled portions with automated stock counts.
* **Administrative Table Overrides:** Dedicated update routes (`PUT`) to change table numbers and maximum seat capacities on the fly.
* **Zero Setup Overhead:** Built-in automatic database initialization pre-seeded with mock test data inside an optimized in-memory SQLite database instance.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Framework:** Flask
* **ORM:** Flask-SQLAlchemy
* **Database:** SQLite (In-Memory `sqlite:///:memory:`)

---

## 📂 Project Structure

```text
CodeAlpha_Restaurant_Management_System/
│
├── app.py              # Main application entry point containing models, logic, and routes
├── README.md           # Documentation and API testing guide
└── requirements.txt    # Project dependencies
