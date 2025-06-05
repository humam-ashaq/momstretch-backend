
# 🧘‍♀️ MomStretch+ Backend

> Backend API untuk platform *MomStretch+* — bantu ibu pasca-melahirkan tetap bugar dengan rutinitas olahraga personal.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-%20microframework-lightgrey)
![Status](https://img.shields.io/badge/status-development-orange)
![License](https://img.shields.io/badge/license-UNLICENSED-red)

---

## 📌 Ringkasan

MomStretch+ adalah platform kesehatan dan kebugaran berbasis mobile yang didukung dengan model computer vision realtime yang membantu para ibu dalam melakukan gerakan senam, dan didukung oleh backend API modular berbasis Flask. Fokus utamanya adalah menyediakan layanan yang aman, ringan, dan mudah dikembangkan untuk mendukung fitur-fitur pelacakan kebugaran dan rutinitas olahraga.

---

## ✨ Fitur Utama

- 🔐 Autentikasi dengan token dan Fernet encryption
- 🧩 Struktur modular per route
- 🗂️ Middleware untuk logging & proteksi endpoint
- 🔄 CRUD endpoint untuk berbagai entitas
- ⚙️ Utilitas untuk hash dan enkripsi data

---

## ⚙️ Teknologi

| Stack        | Teknologi     |
|--------------|----------------|
| Bahasa       | Python 3.x     |
| Framework    | Flask          |
| Keamanan     | Fernet (cryptography) |
| Manajemen    | pip + venv     |
| Deployment   | Local / Cloud-ready |

---

## 🚀 Instalasi

```bash
# Clone repositori
git clone https://github.com/humam-ashaq/momstretch-backend.git
cd momstretch-backend

# Buat virtual environment
python -m venv venv
source venv/bin/activate   # atau venv\Scripts\activate untuk Windows

# Install dependencies
pip install -r requirements.txt

# (Opsional) Generate kunci enkripsi
python generate_fernet_key.py

# Jalankan server
python app.py
```

Server akan berjalan di `http://127.0.0.1:5000/`

---

## 🧱 Struktur Direktori

```
momstretch-backend/
├── app.py                  # Entry point aplikasi
├── db.py                   # Koneksi database
├── routes/                 # Folder endpoint API
├── middleware.py           # Middleware untuk autentikasi
├── utils.py                # Fungsi-fungsi umum
├── generate_fernet_key.py  # Tool enkripsi
├── requirements.txt        # Dependensi Python
```

---

## 🧪 Contoh Endpoint

> Tambahkan dokumentasi Swagger/OpenAPI jika tersedia.

| Method | Endpoint          | Deskripsi             |
|--------|-------------------|------------------------|
| GET    | `/profile`        | Mendapatkan profile user |
| POST   | `/login`          | Login dan dapatkan token |
| ...    | ...               | ...                    |

---

## 🧑‍💻 Kontribusi

Kami membuka kontribusi dari komunitas:

1. Fork repo ini
2. Buat branch baru (`feature/fitur-baru`)
3. Commit perubahan
4. Buka Pull Request

---

## 📄 Lisensi

Lisensi belum ditentukan. Silakan tambahkan file `LICENSE` jika diperlukan.

---

## 👨‍💻 Author
  
📎 [Humam Asathin Haqqani](https://github.com/humam-ashaq)
📎 [Asih Rahmawati](https://github.com/Asihraa)


---

> Dibuat dengan ❤️ untuk mendukung gaya hidup sehat ibu-ibu di seluruh dunia.
