import traceback
from flask import Blueprint, request, jsonify
from db import stretching_collection, movement_collection
from middleware import require_api_key
from bson import ObjectId

stretching_bp = Blueprint('stretching', __name__)

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