from flask import Flask, request, jsonify
from flask_cors import CORS
from db import users_collection
from utils import hash_password, verify_password, generate_token, verify_token
from bson import ObjectId
from dotenv import load_dotenv
import os
import json
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import traceback

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization", "x-api-key"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# Initialize Firebase Admin
try:
    firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
    if not firebase_creds:
        raise Exception("FIREBASE_CREDENTIALS environment variable not set")
    
    cred_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase Admin: {e}")
    # You might want to exit here if Firebase is critical
    # exit(1)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('x-api-key')
        if not client_key:
            return jsonify({'message': 'API Key diperlukan'}), 403
        if client_key != API_KEY:
            print(f"Invalid API Key: {client_key}")
            return jsonify({'message': 'API Key tidak valid'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
@require_api_key
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak valid'}), 400
            
        email = data.get('email')
        password = data.get('password')
        nama = data.get('nama')

        if not all([email, password, nama]):
            return jsonify({'message': 'Semua field harus diisi'}), 400

        if users_collection.find_one({'email': email}):
            return jsonify({'message': 'Email sudah terdaftar'}), 400

        hashed = hash_password(password)
        users_collection.insert_one({
            'email': email,
            'password': hashed,
            'nama': nama
        })

        return jsonify({'message': 'Registrasi berhasil'}), 201
    except Exception as e:
        print(f"Register error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@app.route('/login', methods=['POST'])
@require_api_key
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak valid'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email dan password harus diisi'}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'message': 'Email tidak ditemukan'}), 404

        if not verify_password(user['password'], password):
            return jsonify({'message': 'Password salah'}), 401

        token = generate_token(user['_id'])
        print(f"Login successful for {email}, token: {token[:20]}...")

        return jsonify({'token': token, 'nama': user['nama']}), 200
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@app.route('/login_oauth', methods=['POST'])
@require_api_key
def login_oauth():
    try:
        print("OAuth login request received")
        data = request.get_json()
        
        if not data:
            print("No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
        
        firebase_token = data.get('firebase_token')
        if not firebase_token:
            print("No firebase_token in request")
            return jsonify({'message': 'Firebase token diperlukan'}), 400

        print(f"Received firebase token (length: {len(firebase_token)})")

        # Verify Firebase token
        try:
            decoded = firebase_auth.verify_id_token(firebase_token)
            print(f"Firebase token verified successfully for UID: {decoded.get('uid')}")
        except firebase_auth.InvalidIdTokenError as e:
            print(f"Invalid Firebase token: {e}")
            return jsonify({'message': 'Token Firebase tidak valid'}), 401
        except firebase_auth.ExpiredIdTokenError as e:
            print(f"Expired Firebase token: {e}")
            return jsonify({'message': 'Token Firebase sudah kadaluarsa'}), 401
        except Exception as e:
            print(f"Firebase token verification error: {e}")
            return jsonify({'message': 'Gagal memverifikasi token Firebase'}), 401

        email = decoded.get('email')
        name = decoded.get('name', decoded.get('email', 'Pengguna Google'))
        firebase_uid = decoded.get('uid')

        if not email:
            print("No email in Firebase token")
            return jsonify({'message': 'Email tidak ditemukan dalam token'}), 400

        print(f"Processing OAuth login for email: {email}")

        # Find or create user
        user = users_collection.find_one({'email': email})
        if not user:
            print(f"Creating new user for {email}")
            user_data = {
                'email': email,
                'nama': name,
                'provider': 'google',
                'firebase_uid': firebase_uid
            }
            result = users_collection.insert_one(user_data)
            user = users_collection.find_one({'_id': result.inserted_id})
        else:
            print(f"User found: {email}")
            # Update firebase_uid if not present
            if 'firebase_uid' not in user:
                users_collection.update_one(
                    {'_id': user['_id']},
                    {'$set': {'firebase_uid': firebase_uid}}
                )

        # Generate local token
        token = generate_token(user['_id'])
        print(f"OAuth login successful for {email}")
        
        return jsonify({
            'token': token, 
            'nama': user['nama']
        }), 200

    except Exception as e:
        print(f"OAuth login error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server saat login OAuth'}), 500

@app.route('/profile', methods=['GET'])
@require_api_key
def profile():
    try:
        auth_header = request.headers.get('Authorization')
        print(f"Auth Header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        token = auth_header.split(' ')[1]
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'message': 'Token tidak valid'}), 401

        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        return jsonify({
            'nama': user['nama'],
            'email': user['email'],
            'usia': user.get('usia'),
            'foto_profil': user.get('foto_profil')
        }), 200
    except Exception as e:
        print(f"Profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@app.route('/profile', methods=['PUT'])
@require_api_key
def update_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token diperlukan'}), 401

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'message': 'Token tidak valid atau expired'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'message': 'Data tidak valid'}), 400
            
        usia = data.get('usia')
        foto_profil = data.get('foto_profil')

        update_fields = {}
        if usia is not None:
            update_fields['usia'] = usia
        if foto_profil is not None:
            update_fields['foto_profil'] = foto_profil

        if not update_fields:
            return jsonify({'message': 'Tidak ada data untuk diperbarui'}), 400

        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_fields}
        )

        if result.matched_count == 0:
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        return jsonify({'message': 'Profil berhasil diperbarui'})
    except Exception as e:
        print(f"Update profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@app.route('/profile', methods=['DELETE'])
@require_api_key
def delete_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)

        if not user_id:
            return jsonify({'message': 'Token tidak valid atau expired'}), 401

        result = users_collection.delete_one({'_id': ObjectId(user_id)})

        if result.deleted_count == 0:
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        return jsonify({'message': 'Akun berhasil dihapus'}), 200
    except Exception as e:
        print(f"Delete profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint tidak ditemukan'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Terjadi kesalahan server internal'}), 500

if __name__ == '__main__':
    print(f"Starting Flask app with API_KEY: {'*' * len(API_KEY) if API_KEY else 'NOT SET'}")
    app.run(debug=True, host='0.0.0.0', port=5000)

# url ngrok= https://externally-popular-adder.ngrok-free.app