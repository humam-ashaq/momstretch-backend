from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials
import traceback
# Import blueprints
from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.main_routes import main_bp

load_dotenv()
API_KEY = os.getenv("API_KEY")

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

    # Initialize Firebase Admin
    try:
        firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
        if not firebase_creds:
            raise Exception("FIREBASE_CREDENTIALS environment variable not set")
        
        cred_dict = json.loads(firebase_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")

    # Add request logging middleware
    @app.before_request
    def log_request():
        print(f"\n=== Incoming Request ===")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers: {dict(request.headers)}")
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"Starting Flask app...")
    print(f"API_KEY: {'SET' if API_KEY else 'NOT SET'}")
    print(f"Firebase Admin: {'Initialized' if firebase_admin._apps else 'Not initialized'}")
    app.run(debug=True, host='0.0.0.0', port=5000)