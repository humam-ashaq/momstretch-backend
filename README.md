# 🧘‍♀️ MomStretch+ Backend

> Backend API for the *MomStretch+* platform — helping postpartum moms stay fit with personalized workout routines.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-%20microframework-lightgrey)
![Status](https://img.shields.io/badge/status-development-orange)
![License](https://img.shields.io/badge/license-UNLICENSED-red)

---

## 📌 Overview

MomStretch+ is a mobile-based health and fitness platform supported by a real-time computer vision model that assists mothers in performing exercise routines. It is backed by a modular Flask-based backend API. The main focus is to provide a secure, lightweight, and easily extensible service to support fitness tracking and workout routine features.

---

## ✨ Key Features

- 🔐 Authentication using token and Fernet encryption
- 🧩 Modular structure per route
- 🗂️ Middleware for logging & endpoint protection
- 🔄 CRUD endpoints for various entities
- ⚙️ Utilities for hashing and data encryption

---

## ⚙️ Technology Stack (Backend)

| Layer         | Technology          |
|---------------|----------------------|
| Language      | Python 3.x           |
| Framework     | Flask                |
| Security      | Fernet (cryptography)|
| Management    | pip + venv           |
| Deployment    | Local / Cloud-ready  |

> For frontend stack, see: [momstretch](https://github.com/humam-ashaq/momstretch)

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/humam-ashaq/momstretch-backend.git
cd momstretch-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# (Optional) Generate encryption key
python generate_fernet_key.py

# Run the server
python app.py
```

Server will run at `http://127.0.0.1:5000/`

---

## 🧱 Project Structure

```
momstretch-backend/
├── app.py                  # Application entry point
├── db.py                   # Database connection
├── routes/                 # API endpoint folder
├── middleware.py           # Middleware for authentication
├── utils.py                # Utility functions
├── generate_fernet_key.py  # Encryption tool
├── requirements.txt        # Python dependencies
```

---

## 🧪 Sample Endpoints

> Add Swagger/OpenAPI documentation if available.

| Method | Endpoint          | Description             |
|--------|-------------------|--------------------------|
| GET    | `/profile`        | Get user profile         |
| POST   | `/login`          | Login and receive token  |
| ...    | ...               | ...                      |

---

## 🧑‍💻 Contribution

We welcome community contributions:

1. Fork this repo
2. Create a new branch (`feature/new-feature`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

License not yet specified. Please add a `LICENSE` file if needed.

---

## 👨‍💻 Authors

📎 [Humam Asathin Haqqani](https://github.com/humam-ashaq)  
📎 [Asih Rahmawati](https://github.com/Asihraa)

---

> Made with ❤️ to support a healthy lifestyle for moms around the world.
