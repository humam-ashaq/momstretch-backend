from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from dotenv import load_dotenv
import os

SECRET_KEY = os.getenv("SECRET_KEY")  # Ubah ini pakai key yang aman!

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hash_password_db, input_password):
    return check_password_hash(hash_password_db, input_password)

def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token kedaluwarsa
    except jwt.InvalidTokenError:
        return None  # Token tidak valid