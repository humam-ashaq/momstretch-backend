from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials
import traceback

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.main_routes import main_bp
from routes.article_routes import article_bp
from routes.stretching_routes import stretching_bp
from routes.epds_routes import epds_bp

load_dotenv()
API_KEY = os.getenv("API_KEY")

# ==========================================
# 1. INISIALISASI FIREBASE (GLOBAL SCOPE)
# ==========================================

# Cek nama variable, bisa FIREBASE_KEY atau FIREBASE_CREDENTIALS
raw_cred = os.getenv('FIREBASE_KEY') or os.getenv('FIREBASE_CREDENTIALS')

if not raw_cred:
    print("❌ FATAL: Environment Variable Firebase tidak ditemukan!")
    raise ValueError("Firebase Environment Variable Missing")

try:
    # 1. Parsing Pertama
    cred_dict = json.loads(raw_cred)

    # 2. FIX CRITICAL ERROR: DOUBLE PARSING
    # Jika hasil parsing masih berupa string (karena ada kutip dobel di env var),
    # kita parse sekali lagi agar menjadi Dictionary.
    if isinstance(cred_dict, str):
        print("⚠️ Mendeteksi double-encoded JSON, melakukan parsing ulang...")
        cred_dict = json.loads(cred_dict)

    # 3. FIX BUG PRIVATE KEY
    # Pastikan ini sudah berupa dictionary sebelum mengakses key
    if isinstance(cred_dict, dict) and 'private_key' in cred_dict:
        cred_dict['private_key'] = cred_dict['private_key'].replace('\\n', '\n')
    
    # 4. Initialize App
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ SUCCESS: Firebase Admin initialized successfully!")
        
except Exception as e:
    print(f"❌ CRITICAL ERROR initializing Firebase: {str(e)}")
    traceback.print_exc()
    # Paksa berhenti agar kita bisa lihat lognya di deployment
    raise e

# ==========================================
# 2. APP FACTORY
# ==========================================

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
                if body and 'firebase_token' in body:
                    body_copy = body.copy()
                    body_copy['firebase_token'] = "HIDDEN_TOKEN"
                    print(f"Body: {body_copy}")
                else:
                    print(f"Body: {body}")
            except:
                pass

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
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

# ==========================================
# 3. ENTRY POINT
# ==========================================

app = create_app()

if __name__ == '__main__':
    print(f"Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=5000)
