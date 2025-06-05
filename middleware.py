from flask import request, jsonify
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_key = request.headers.get('x-api-key')
        if not client_key:
            print("ERROR: No API Key provided")
            return jsonify({'message': 'API Key diperlukan'}), 403
        if client_key != API_KEY:
            print(f"ERROR: Invalid API Key provided: {client_key}")
            return jsonify({'message': 'API Key tidak valid'}), 403
        print("API Key validation successful")
        return f(*args, **kwargs)
    return decorated_function