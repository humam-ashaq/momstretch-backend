from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import jwt
import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage
import random

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
FERNET_KEY = os.getenv("FERNET_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS") # verif email
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Validasi bahwa kunci tidak kosong
if not SECRET_KEY or not FERNET_KEY:
    raise ValueError("SECRET_KEY dan FERNET_KEY harus diatur di .env")

fernet = Fernet(FERNET_KEY.encode())

# Password hashing
def hash_password(password):
    return generate_password_hash(password)

def verify_password(hash_password_db, input_password):
    return check_password_hash(hash_password_db, input_password)

# Enkripsi dan dekripsi data
def encrypt_data(data):
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token):
    return fernet.decrypt(token.encode()).decode()

# JWT token generation
def generate_token(user_id):
    encrypted_id = encrypt_data(str(user_id))
    payload = {
        'data': encrypted_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# JWT token verification
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        decrypted_id = decrypt_data(payload['data'])
        return decrypted_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None

# Fungsi OTP
def generate_otp():
    return str(random.randint(100000, 999999))  # OTP 6 digit

def send_otp_email(to_email, otp_code):
    msg = EmailMessage()
    msg['Subject'] = 'Kode OTP Verifikasi MomStretch+'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f'''
Hai!

Kode OTP kamu adalah: {otp_code}

Kode ini hanya berlaku selama 10 menit.
Jangan bagikan kode ini ke siapa pun.

Salam hangat,
Tim MomStretch+
''')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)