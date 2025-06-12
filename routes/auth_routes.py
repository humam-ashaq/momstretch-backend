from flask import Blueprint, request, jsonify
from db import users_collection, history_collection
from utils import hash_password, verify_password, generate_token, send_otp_email, generate_otp, verify_token
from middleware import require_api_key
from firebase_admin import auth as firebase_auth
import traceback
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@require_api_key
def register():
    try:
        print("Processing registration request...")
        data = request.get_json()
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
            
        email = data.get('email')
        password = data.get('password')
        nama = data.get('nama')

        if not all([email, password, nama]):
            print("ERROR: Missing required fields")
            return jsonify({'message': 'Semua field harus diisi'}), 400

        if users_collection.find_one({'email': email}):
            print(f"ERROR: Email already exists: {email}")
            return jsonify({'message': 'Email sudah terdaftar'}), 400

        hashed = hash_password(password)
        otp_code = generate_otp()
        otp_expired = datetime.utcnow() + timedelta(minutes=10)

        user = {
            'email': email,
            'password': hashed,
            'nama': nama,
            'program': '',
            'is_verified': False,
            'otp_code': otp_code,
            'otp_expired': otp_expired
        }

        users_collection.insert_one(user)
        send_otp_email(email, otp_code)

        print(f"User registered successfully: {email}")
        return jsonify({'message': 'Kode OTP telah dikirim ke email'}), 201
        
    except Exception as e:
        print(f"❌ Error saat register: {e}")
        return jsonify({'message': 'Terjadi kesalahan di server'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
@require_api_key
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'message': 'Email tidak ditemukan'}), 404

    if user.get('is_verified'):
        return jsonify({'message': 'Akun sudah terverifikasi'}), 400

    if user.get('otp_code') != otp:
        return jsonify({'message': 'Kode OTP salah'}), 400

    if datetime.utcnow() > user.get('otp_expired'):
        return jsonify({'message': 'Kode OTP sudah kedaluwarsa'}), 400

    users_collection.update_one({'email': email}, {
        '$set': {'is_verified': True},
        '$unset': {'otp_code': "", 'otp_expired': ""}
    })

    return jsonify({'message': 'Verifikasi berhasil'}), 200

@auth_bp.route('/login', methods=['POST'])
@require_api_key
def login():
    try:
        print("Processing login request...")
        data = request.get_json()
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            print("ERROR: Missing email or password")
            return jsonify({'message': 'Email dan password harus diisi'}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            print(f"ERROR: Email not found: {email}")
            return jsonify({'message': 'Email tidak ditemukan'}), 404
        
        if not user.get('is_verified'):
            return jsonify({'message': 'Email belum diverifikasi'}), 403

        if not verify_password(user['password'], password):
            print(f"ERROR: Wrong password for: {email}")
            return jsonify({'message': 'Password salah'}), 401

        token = generate_token(user['_id'])
        print(f"Login successful for {email}, token: {token[:20]}...")

        # Simpan riwayat login
        history_collection.insert_one({
            'user_id': str(user['_id']),
            'timestamp': datetime.utcnow(),
            'device': request.headers.get('User-Agent'),
            'ip': request.remote_addr,
        })

        return jsonify({'token': token, 'nama': user['nama']}), 200
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@auth_bp.route('/login_oauth', methods=['POST', 'OPTIONS'])
@require_api_key
def login_oauth():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-api-key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    try:
        print("=== Processing OAuth login request ===")
        
        # Validate content type
        if not request.is_json:
            print("ERROR: Request is not JSON")
            return jsonify({'message': 'Content-Type harus application/json'}), 400
        
        data = request.get_json()
        
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
        
        firebase_token = data.get('firebase_token')
        if not firebase_token:
            print("ERROR: No firebase_token in request")
            return jsonify({'message': 'Firebase token diperlukan'}), 400

        print(f"Received firebase token (length: {len(firebase_token)})")

        # Verify Firebase token
        try:
            print("Verifying Firebase token...")
            decoded = firebase_auth.verify_id_token(firebase_token, check_revoked=False, clock_skew_seconds=60)
            print(f"Firebase token verified successfully for UID: {decoded.get('uid')}")
            print(f"Token contains email: {decoded.get('email')}")
        except firebase_auth.InvalidIdTokenError as e:
            error_msg = str(e)
            print(f"ERROR: Invalid Firebase token: {error_msg}")
            
            # Handle specific clock skew errors
            if "used too early" in error_msg or "clock" in error_msg.lower():
                print("Clock skew detected, retrying with more tolerance...")
                try:
                    # Retry with more generous clock skew tolerance
                    decoded = firebase_auth.verify_id_token(firebase_token, check_revoked=False, clock_skew_seconds=300)
                    print("Token verified successfully with clock skew tolerance")
                except Exception as retry_e:
                    print(f"Retry failed: {retry_e}")
                    return jsonify({'message': 'Sinkronisasi waktu bermasalah. Coba lagi dalam beberapa detik.'}), 401
            else:
                return jsonify({'message': 'Token Firebase tidak valid'}), 401
        except firebase_auth.ExpiredIdTokenError as e:
            print(f"ERROR: Expired Firebase token: {e}")
            return jsonify({'message': 'Token Firebase sudah kadaluarsa'}), 401
        except Exception as e:
            print(f"ERROR: Firebase token verification error: {e}")
            traceback.print_exc()
            return jsonify({'message': 'Gagal memverifikasi token Firebase'}), 401

        email = decoded.get('email')
        name = decoded.get('name', decoded.get('email', 'Pengguna Google'))
        firebase_uid = decoded.get('uid')

        if not email:
            print("ERROR: No email in Firebase token")
            return jsonify({'message': 'Email tidak ditemukan dalam token'}), 400

        print(f"Processing OAuth login for email: {email}")

        # Find or create user
        try:
            user = users_collection.find_one({'email': email})
            if not user:
                print(f"Creating new user for {email}")
                user_data = {
                    'email': email,
                    'nama': name,
                    'program': '',
                    'provider': 'google',
                    'firebase_uid': firebase_uid
                }
                result = users_collection.insert_one(user_data)
                user = users_collection.find_one({'_id': result.inserted_id})
                print(f"New user created with ID: {result.inserted_id}")
            else:
                print(f"Existing user found: {email}")
                # Update firebase_uid if not present
                if 'firebase_uid' not in user:
                    users_collection.update_one(
                        {'_id': user['_id']},
                        {'$set': {'firebase_uid': firebase_uid}}
                    )
                    print("Updated user with Firebase UID")
        except Exception as e:
            print(f"ERROR: Database operation failed: {e}")
            traceback.print_exc()
            return jsonify({'message': 'Terjadi kesalahan database'}), 500

        # Generate local token
        try:
            token = generate_token(user['_id'])
            print(f"Generated token for user: {email}")
        except Exception as e:
            print(f"ERROR: Token generation failed: {e}")
            traceback.print_exc()
            return jsonify({'message': 'Gagal membuat token'}), 500
        
        response_data = {
            'token': token, 
            'nama': user['nama']
        }
        
        print(f"OAuth login successful for {email}")
        print(f"Response data: {response_data}")

        # Simpan riwayat login
        history_collection.insert_one({
            'user_id': str(user['_id']),
            'timestamp': datetime.utcnow(),
            'device': request.headers.get('User-Agent'),
            'ip': request.remote_addr,
        })
        
        return jsonify(response_data), 200

    except Exception as e:
        print(f"CRITICAL ERROR in OAuth login: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server saat login OAuth'}), 500

@auth_bp.route('/login-history', methods=['GET'])
@require_api_key
def get_login_history():
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            print("ERROR: No valid Authorization header")
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        token = auth_header.split(' ')[1]
        user_id = verify_token(token)

        if not user_id:
            print("ERROR: Token verification failed")
            return jsonify({'message': 'Token tidak valid'}), 401
        
        history = list(history_collection.find({'user_id': user_id}).sort('timestamp', -1))
        for h in history:
            h['_id'] = str(h['_id'])
            h['timestamp'] = h['timestamp'].isoformat()
        return jsonify(history) 
    except Exception as e:
        print(f"History error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500