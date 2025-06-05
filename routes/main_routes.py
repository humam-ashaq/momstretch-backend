from flask import Blueprint, jsonify
from middleware import require_api_key

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
@require_api_key
def health_check():
    return jsonify({'status': 'OK', 'message': 'Server is running'}), 200