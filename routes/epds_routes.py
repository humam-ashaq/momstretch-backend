from datetime import datetime
import traceback
from flask import Blueprint, request, jsonify
from db import epds_collection
from utils import verify_token
from middleware import require_api_key
from bson import ObjectId

epds_bp = Blueprint('epds', __name__)

@epds_bp.route('/api/epds', methods=['POST'])
@require_api_key
def save_epds_result():
    try:
        # Verifikasi token untuk mendapatkan user_id
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token tidak ditemukan'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token) # Dapatkan user_id dari token
        
        if not user_id:
            return jsonify({'message': 'Token tidak valid'}), 401

        data = request.get_json()
        score = data['score']

        # Menentukan hasil berdasarkan skor
        result_text = ''
        if score >= 13:
            result_text = 'Beresiko Tinggi Depresi'
        elif score >= 9:
            result_text = 'Berkemungkinan Depresi'
        else:
            result_text = 'Resiko Rendah'

        # Membuat dokumen baru untuk disimpan
        new_record = {
            'userId': user_id,
            'score': score,
            'result': result_text,
            'date': datetime.utcnow() # Simpan waktu saat ini
        }

        # Simpan ke database
        epds_collection.insert_one(new_record)

        return jsonify({'message': 'Hasil EPDS berhasil disimpan'}), 201
    except Exception as e:
        print(f"❌ Error saat menyimpan: {e}")
        return jsonify({'message': 'Terjadi kesalahan di server'}), 500

@epds_bp.route('/api/epds/history', methods=['GET'])
@require_api_key
def get_epds_history():
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
        
        records = list(epds_collection.find({'userId': user_id}).sort('date', 1))
    
        if not records:
            return jsonify([]), 200 # Kembalikan array kosong jika tidak ada riwayat

        # Format data agar hanya berisi skor (sesuai kebutuhan LineChart Anda)
        # Jika Anda butuh tanggalnya juga, Anda bisa mengirim seluruh record
        score_history = [record['score'] for record in records]

        return jsonify(score_history), 200
    except Exception as e:
        print(f"History error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500