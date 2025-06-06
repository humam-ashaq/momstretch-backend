from flask import Blueprint, request, jsonify
from db import users_collection
from utils import verify_token
from middleware import require_api_key
from bson import ObjectId
import traceback

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@require_api_key
def get_profile():
    try:
        print("Processing profile request...")
        auth_header = request.headers.get('Authorization')
        print(f"Auth Header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print("ERROR: No valid Authorization header")
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        token = auth_header.split(' ')[1]
        user_id = verify_token(token)

        if not user_id:
            print("ERROR: Token verification failed")
            return jsonify({'message': 'Token tidak valid'}), 401

        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            print(f"ERROR: User not found for ID: {user_id}")
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404
        
        print(f"Profile request successful for user: {user['email']}")
        return jsonify({
            'nama': user['nama'],
            'email': user['email'],
            'program': user['program'],
            'usia': user.get('usia'),
            'foto_profil': user.get('foto_profil')
        }), 200
    except Exception as e:
        print(f"Profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@profile_bp.route('/profile', methods=['PUT'])
@require_api_key
def update_profile():
    try:
        print("Processing profile update request...")
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("ERROR: No valid Authorization header")
            return jsonify({'message': 'Token diperlukan'}), 401

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)

        if not user_id:
            print("ERROR: Token verification failed")
            return jsonify({'message': 'Token tidak valid atau expired'}), 401

        data = request.get_json()
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
            
        usia = data.get('usia')
        foto_profil = data.get('foto_profil')

        update_fields = {}
        if usia is not None:
            update_fields['usia'] = usia
        if foto_profil is not None:
            update_fields['foto_profil'] = foto_profil

        if not update_fields:
            print("ERROR: No fields to update")
            return jsonify({'message': 'Tidak ada data untuk diperbarui'}), 400

        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_fields}
        )

        if result.matched_count == 0:
            print(f"ERROR: User not found for update: {user_id}")
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        print(f"Profile updated successfully for user: {user_id}")
        return jsonify({'message': 'Profil berhasil diperbarui'})
    except Exception as e:
        print(f"Update profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    
@profile_bp.route('/program', methods=['PUT'])
@require_api_key
def update_program():
    try:
        print("Processing profile update request...")
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("ERROR: No valid Authorization header")
            return jsonify({'message': 'Token diperlukan'}), 401

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)

        if not user_id:
            print("ERROR: Token verification failed")
            return jsonify({'message': 'Token tidak valid atau expired'}), 401

        data = request.get_json()
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({'message': 'Data tidak valid'}), 400
            
        program = data.get('program')

        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'program': program}}
        )

        if result.matched_count == 0:
            print(f"ERROR: User not found for update: {user_id}")
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        print(f"Programe updated successfully for user: {user_id}")
        return jsonify({'message': 'Program berhasil diperbarui'})
    except Exception as e:
        print(f"Update program error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@profile_bp.route('/profile', methods=['DELETE'])
@require_api_key
def delete_profile():
    try:
        print("Processing profile deletion request...")
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            print("ERROR: No valid Authorization header")
            return jsonify({'message': 'Token tidak ditemukan'}), 401

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)

        if not user_id:
            print("ERROR: Token verification failed")
            return jsonify({'message': 'Token tidak valid atau expired'}), 401

        result = users_collection.delete_one({'_id': ObjectId(user_id)})

        if result.deleted_count == 0:
            print(f"ERROR: User not found for deletion: {user_id}")
            return jsonify({'message': 'Pengguna tidak ditemukan'}), 404

        print(f"Profile deleted successfully for user: {user_id}")
        return jsonify({'message': 'Akun berhasil dihapus'}), 200
    except Exception as e:
        print(f"Delete profile error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500