import traceback
import cv2
from flask import Blueprint, request, jsonify
import numpy as np
from db import stretching_collection, movement_collection, stretch_history_collection, users_collection
from middleware import require_api_key
from utils import verify_token
from bson import ObjectId
import base64
import tensorflow as tf
import mediapipe as mp
from datetime import datetime
from pytz import timezone 
import pytz

stretching_bp = Blueprint('stretching', __name__)

model = tf.keras.models.load_model('model.h5')

labels = [
    "resistance_fight", "slide_out", "pelvic_tilts", "heel_slides",
    "vacuum_abs_standing", "Pelvic Tilts (Posisi Merangkak)", "Abdominal Brace (Posisi Berbaring Miring)", "Heel Slides",
    "Knee Taps to Kickbacks", "Leg Lifts with Brace", "Arm Lifts with Brace", "Double Leg Lifts (Tumit Bersama)",
    "Top Leg Lifts", "Tabletop Leg Lifts(progresi)", "Knee Drops (Kaki & Lutut Bersama)", "curl to side raises", "push and pull", "twist and pull", "single lat and oblique pulls", "single arm tricep extention", "6. Squats", "5. March with Arm Raises", "1. Warm-up running in place", "3. Step and Kick Back", "2. Marching Arm & Leg Lifts", "8. Standing Abdominal Crunch", "10. Calf Raises with Arm Swings", "9. Mini Squat with Step Backs", "7. Squat Taps", "4. Knee Lifts", "teeter_totter", "Deadbug", "calf stretches", "Bridge", "bridge and feet up", "modified side plank", "pillow_pelvic","slide_dumbbell", "plank_4_leg_dog", "toe_tap", "toe_slide", "leg_pillow_plank", "leg_pillow_tap", "pillow_vacuum_abs", "vacuum_abs_dog"
]

mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

@stretching_bp.route('/api/stretching', methods=['GET'])
@require_api_key
def get_stretching():
    try:
        program_filter = request.args.get('program')

        query = {}
        
        if program_filter:
            query['program'] = program_filter

        projection = {
            '_id': 1,
            'stretching': 1,
            'program': 1,
            'imageUrl': 1,
            'stretchingDesc': 1,
            'duration': 1, 
        }

        stretchings_cursor = stretching_collection.find(query, projection)
        stretchings = list(stretchings_cursor)

        for stretching in stretchings:
            stretching['_id'] = str(stretching['_id'])

        return jsonify(stretchings), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500

@stretching_bp.route('/api/stretching/<stretching_id>', methods=['GET'])
@require_api_key
def get_stretching_by_id(stretching_id):
    try:
        if not ObjectId.is_valid(stretching_id):
            return jsonify({'error': 'Invalid stretching id'}), 400
        
        # Ambil semua data karena akan dibutuhkan di detail
        stretching = stretching_collection.find_one({'_id': ObjectId(stretching_id)})

        if not stretching:
            return jsonify({'error': 'Stretching not found'}), 404
        
        stretching['_id'] = str(stretching['_id'])
        
        return jsonify(stretching), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

@stretching_bp.route('/api/movement', methods=['GET'])
@require_api_key
def get_movement():
    try:
        # TAMBAHKAN: Ambil parameter 'stretching' dari query
        stretching_filter = request.args.get('stretching')

        if not stretching_filter:
            return jsonify({'error': 'Parameter "stretching" dibutuhkan'}), 400

        # TAMBAHKAN: Filter movement berdasarkan jenis stretching
        query = {'stretching': stretching_filter}
        
        projection = {
            '_id': 1,
            'movement': 1,
            'imageUrl': 1,
        }

        movements_cursor = movement_collection.find(query, projection)
        movements = list(movements_cursor)

        for movement in movements:
            movement['_id'] = str(movement['_id'])

        return jsonify(movements), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500
    
@stretching_bp.route('/api/movement/<movement_id>', methods=['GET'])
@require_api_key
def get_movement_by_id(movement_id):
    try:
        if not ObjectId.is_valid(movement_id):
            return jsonify({'error': 'Invalid movement id'}), 400
        
        # Ambil semua data karena dibutuhkan di bottom sheet
        movement = movement_collection.find_one({'_id': ObjectId(movement_id)})

        if not movement:
            return jsonify({'error': 'Movement not found'}), 404
        
        movement['_id'] = str(movement['_id'])
        
        return jsonify(movement), 200
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    
def extract_keypoints_from_image(image):
    """Mengekstrak 99 keypoints (x, y, z) dari satu gambar."""
    results = pose_detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if results.pose_landmarks:
        return np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]).flatten()
    else:
        return None

# TAMBAHKAN ENDPOINT BARU INI
@stretching_bp.route('/api/detect', methods=['POST'])
@require_api_key
def detect_pose_api():
    try:
        data = request.get_json()
        if 'image' not in data or 'target_label' not in data:
            return jsonify({'error': 'Data tidak lengkap'}), 400

        img_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        keypoints = extract_keypoints_from_image(frame)
        if keypoints is None:
            return jsonify({'status': '❌ Gagal mendeteksi pose'})

        sequence = np.array([keypoints] * 30)
        prediction = model.predict(np.expand_dims(sequence, axis=0))[0]
        
        target_label = data['target_label']
        if target_label in labels:
            target_index = labels.index(target_label)
            accuracy = float(prediction[target_index]) # Konversi ke float standar Python
            
            print(f"Target: {target_label}, Akurasi: {accuracy:.2f}")
            
            if accuracy > 0.85:
                return jsonify({'status': '✅ Gerakan Sudah Tepat'})
            else:
                return jsonify({'status': '❌ Gerakan Belum Sesuai'})
        else:
            return jsonify({'status': 'Error: Label tidak ditemukan'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Terjadi kesalahan di server: {e}'}), 500
    
@stretching_bp.route('/api/stretch_history', methods=['POST'])
@require_api_key
def add_history():
    try:
        # 1. Ambil token dari header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token tidak ada atau format salah'}), 401

        token = auth_header.split(" ")[1]

        # 2. Panggil fungsi verify_token dari utils
        decrypted_id = verify_token(token)
        if not decrypted_id:
            return jsonify({'error': 'Token tidak valid atau kedaluwarsa'}), 401

        # 3. Cari user di database berdasarkan ID dari token
        user = users_collection.find_one({'_id': ObjectId(decrypted_id)})
        if not user:
            return jsonify({'error': 'User tidak ditemukan'}), 404
        
        user_name = user.get('name', 'Nama Tidak Ditemukan')

        # 4. Lanjutkan logika untuk menyimpan history
        data = request.get_json()
        if not data or 'movement_name' not in data:
            return jsonify({'error': 'Data tidak lengkap'}), 400
            
        movement_name = data['movement_name']

        history_doc = {
            'user_name': user_name,
            'user_id': ObjectId(decrypted_id), # Simpan juga ID user jika perlu
            'movement_name': movement_name,
            'timestamp': datetime.utcnow()
        }

        stretch_history_collection.insert_one(history_doc)

        return jsonify({'message': 'History berhasil disimpan'}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Terjadi kesalahan di server: {e}'}), 500
    
@stretching_bp.route('/api/stretch_history', methods=['GET'])
@require_api_key
def get_history():
    try:
        # 1. Verifikasi token untuk mendapatkan ID user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token tidak ada atau format salah'}), 401

        token = auth_header.split(" ")[1]
        decrypted_id = verify_token(token)
        if not decrypted_id:
            return jsonify({'error': 'Token tidak valid atau kedaluwarsa'}), 401

        # 2. Ambil semua data history untuk user tersebut, urutkan dari yang terbaru
        user_history_cursor = stretch_history_collection.find(
            {'user_id': ObjectId(decrypted_id)}
        ).sort('timestamp', -1) # -1 untuk descending (terbaru dulu)

        history_list = []
        
        # Tentukan zona waktu WIB
        wib = timezone('Asia/Jakarta')

        for doc in user_history_cursor:
            # Format timestamp ke string yang mudah dibaca dalam WIB
            local_time = doc['timestamp'].replace(tzinfo=pytz.utc).astimezone(wib)
            formatted_time = local_time.strftime('%d %B %Y, %H:%M WIB')

            history_list.append({
                'id': str(doc['_id']),
                'movement_name': doc['movement_name'],
                'timestamp': formatted_time
            })

        return jsonify(history_list), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Terjadi kesalahan di server: {e}'}), 500