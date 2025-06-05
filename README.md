# 🧘‍♀️ MomStretch+ Backend

> Backend API untuk platform *MomStretch+* — bantu ibu pasca-melahirkan tetap bugar dengan rutinitas olahraga personal.  
> Backend API for the *MomStretch+* platform — helping postpartum moms stay fit with personalized workout routines.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-%20microframework-lightgrey)
![Status](https://img.shields.io/badge/status-development-orange)
![License](https://img.shields.io/badge/license-UNLICENSED-red)

---

## 📌 Ringkasan / Overview

MomStretch+ adalah platform kesehatan dan kebugaran berbasis mobile yang didukung dengan model computer vision realtime yang membantu para ibu dalam melakukan gerakan senam, dan didukung oleh backend API modular berbasis Flask. Fokus utamanya adalah menyediakan layanan yang aman, ringan, dan mudah dikembangkan untuk mendukung fitur-fitur pelacakan kebugaran dan rutinitas olahraga.  
MomStretch+ is a mobile-based health and fitness platform supported by a real-time computer vision model that assists mothers in performing exercise routines. It is backed by a modular Flask-based backend API. The main focus is to provide a secure, lightweight, and easily extensible service to support fitness tracking and workout routine features.

---

## ✨ Fitur Utama / Key Features

- 🔐 Autentikasi dengan token dan Fernet encryption  
  Authentication using token and Fernet encryption
- 🧩 Struktur modular per route  
  Modular structure per route
- 🗂️ Middleware untuk logging & proteksi endpoint  
  Middleware for logging & endpoint protection
- 🔄 CRUD endpoint untuk berbagai entitas  
  CRUD endpoints for various entities
- ⚙️ Utilitas untuk hash dan enkripsi data  
  Utilities for hashing and data encryption

---

## ⚙️ Teknologi / Technology Stack

| Lapisan        | Teknologi           | Layer         | Technology          |
|----------------|---------------------|---------------|----------------------|
| Bahasa         | Python 3.x          | Language      | Python 3.x           |
| Framework      | Flask               | Framework     | Flask                |
| Keamanan       | Fernet (cryptography)| Security      | Fernet (cryptography)|
| Manajemen      | pip + venv          | Management    | pip + venv           |
| Deployment     | Lokal / Cloud-ready | Deployment    | Local / Cloud-ready  |

---

## 🚀 Instalasi / Installation

```bash
# Clone repositori / Clone the repository
git clone https://github.com/humam-ashaq/momstretch-backend.git
cd momstretch-backend

# Buat virtual environment / Create virtual environment
python -m venv venv
source venv/bin/activate   # atau / or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# (Opsional) Generate kunci enkripsi / (Optional) Generate encryption key
python generate_fernet_key.py

# Jalankan server / Run the server
python app.py
```

Server akan berjalan di `http://127.0.0.1:5000/`  
Server will run at `http://127.0.0.1:5000/`

---

## 🧱 Struktur Direktori / Project Structure

```
momstretch-backend/
├── app.py                  # Entry point aplikasi / Application entry point
├── db.py                   # Koneksi database / Database connection
├── routes/                 # Folder endpoint API / API endpoint folder
├── middleware.py           # Middleware untuk autentikasi / Middleware for authentication
├── utils.py                # Fungsi-fungsi umum / Utility functions
├── generate_fernet_key.py  # Tool enkripsi / Encryption tool
├── requirements.txt        # Dependensi Python / Python dependencies
```

---

## 🧪 Contoh Endpoint / Sample Endpoints

> Tambahkan dokumentasi Swagger/OpenAPI jika tersedia.  
> Add Swagger/OpenAPI documentation if available.

| Method | Endpoint          | Deskripsi / Description        |
|--------|-------------------|--------------------------------|
| GET    | `/profile`        | Mendapatkan profil user / Get user profile |
| POST   | `/login`          | Login dan dapatkan token / Login and receive token |
| ...    | ...               | ...                            |

---

## 🧑‍💻 Kontribusi / Contribution

Kami membuka kontribusi dari komunitas:  
We welcome community contributions:

1. Fork repo ini / Fork this repo  
2. Buat branch baru (`feature/fitur-baru`) / Create a new branch (`feature/new-feature`)  
3. Commit perubahan / Commit your changes  
4. Buka Pull Request / Open a Pull Request

---

## 📄 Lisensi / License

Lisensi belum ditentukan. Silakan tambahkan file `LICENSE` jika diperlukan.  
License not yet specified. Please add a `LICENSE` file if needed.

---

## 👨‍💻 Author

📎 [Humam Asathin Haqqani](https://github.com/humam-ashaq)  
📎 [Asih Rahmawati](https://github.com/Asihraa)

---

> Dibuat dengan ❤️ untuk mendukung gaya hidup sehat ibu-ibu di seluruh dunia.  
> Made with ❤️ to support a healthy lifestyle for moms around the world.
