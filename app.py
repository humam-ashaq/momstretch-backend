from flask import Flask, request, jsonify
from flask_cors import CORS
from db import users_collection
from utils import hash_password, verify_password, generate_token, verify_token
from bson import ObjectId
from dotenv import load_dotenv
import os
from functools import wraps

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

#wrap fungsi untuk require api key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('x-api-key')
        if client_key != API_KEY:
            print(client_key)
            return jsonify({'message': 'API Key tidak valid'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
@require_api_key
def register():
    #menerima data dari client
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nama = data.get('nama')

    #jika ada data kosong
    if not all([email, password, nama]):
        return jsonify({'message': 'Semua field harus diisi'}), 400

    #jika data email sudah ada di db
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email sudah terdaftar'}), 400

    #hash password
    hashed = hash_password(password)
    #insert data ke db
    users_collection.insert_one({
        'email': email,
        'password': hashed,
        'nama': nama
    })

    return jsonify({'message': 'Registrasi berhasil'}), 201

@app.route('/login', methods=['POST'])
@require_api_key
def login():
    #menerima data dari client
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    #mengambil data dari db berdasarkan email
    user = users_collection.find_one({'email': email})

    if not user:
        return jsonify({'message': 'Email tidak ditemukan'}), 404

    if not verify_password(user['password'], password):
        return jsonify({'message': 'Password salah'}), 401

    token = generate_token(user['_id'])

    print(f"Token: {token}")

    return jsonify({'token': token, 'nama': user['nama']}), 200

@app.route('/profile', methods=['GET'])
@require_api_key
def profile():
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
        'email': user['email']
    }), 200

@app.route('/profile', methods=['PUT'])
@require_api_key
def update_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Token diperlukan'}), 401

    token = auth_header.split(" ")[1]
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'message': 'Token tidak valid atau expired'}), 401

    data = request.get_json()   
    usia = data.get('usia')
    foto_profil = data.get('foto_profil')

    update_fields = {}
    if usia is not None:
        update_fields['usia'] = usia
    if foto_profil is not None:
        update_fields['foto_profil'] = foto_profil

    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': update_fields}
    )

    return jsonify({'message': 'Profil berhasil diperbarui'})

@app.route('/profile', methods=['DELETE'])
@require_api_key
def delete_profile():
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

#url ngrok= https://externally-popular-adder.ngrok-free.app 