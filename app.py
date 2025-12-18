from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials
import traceback

from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.main_routes import main_bp
from routes.article_routes import article_bp
from routes.stretching_routes import stretching_bp
from routes.epds_routes import epds_bp

load_dotenv()
API_KEY = os.getenv("API_KEY")

raw_cred = os.getenv('FIREBASE_KEY') or os.getenv('FIREBASE_CREDENTIALS')

if not raw_cred:
    print("❌ FATAL: Environment Variable Firebase tidak ditemukan!")
    # Kita raise error agar deployment GAGAL. 
    # Lebih baik gagal deploy daripada aplikasi jalan tapi error saat login.
    raise ValueError("Firebase Environment Variable Missing")

try:
    # A. Parse JSON string ke Dictionary Python
    cred_dict = json.loads(raw_cred)

    # B. FIX BUG PRIVATE KEY: Ubah double slash \\n menjadi single \n
    if 'private_key' in cred_dict:
        cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')

    # C. Initialize App (Cek dulu biar gak double init)
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ SUCCESS: Firebase Admin initialized successfully!")
        
except Exception as e:
    print(f"❌ CRITICAL ERROR initializing Firebase: {str(e)}")
    traceback.print_exc()
    # Paksa berhenti jika Firebase gagal init
    raise e

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization", "x-api-key"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })

    # Add request logging middleware
    @app.before_request
    def log_request():
        print(f"\n➡️ [{request.method}] {request.url}")
        if request.is_json:
            try:
                body = request.get_json()
                # Don't log sensitive data in full
                if 'firebase_token' in body:
                    body_copy = body.copy()
                    body_copy['firebase_token'] = f"[TOKEN:{len(body['firebase_token'])} chars]"
                    print(f"Body: {body_copy}")
                else:
                    print(f"Body: {body}")
            except:
                print("Body: [Unable to parse JSON]")
        print("=====================\n")

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        print(f"404 Error: {request.url} not found")
        return jsonify({'message': 'Endpoint tidak ditemukan'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 Error: {error}")
        return jsonify({'message': 'Terjadi kesalahan server internal'}), 500

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(stretching_bp)
    app.register_blueprint(epds_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    print(f"Starting Flask app...")
    print(f"API_KEY: {'SET' if API_KEY else 'NOT SET'}")
    print(f"Firebase Admin: {'Initialized' if firebase_admin._apps else 'Not initialized'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
