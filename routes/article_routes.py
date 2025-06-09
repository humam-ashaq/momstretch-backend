from flask import Blueprint, request, jsonify
from db import articles_collection, visualization_collection
from middleware import require_api_key
from bson import ObjectId
import traceback

article_bp = Blueprint('article', __name__)

# Endpoint untuk daftar artikel (tanpa content)
@article_bp.route('/articles', methods=['GET'])
@require_api_key
def get_articles():
    try:
        print("Processing articles list request...")

        # Parameter untuk limit (opsional)
        limit = request.args.get('limit', default=None, type=int)
        
        # Ambil hanya kolom untuk list, exclude content
        projection = {
            '_id': 1,  # Include _id untuk reference
            'title': 1,
            'image_url': 1,
            'month_year': 1,
            'published_date': 1
        }
        
        # Query dengan sorting berdasarkan _id descending (terbaru dulu)
        # Jika ada field created_at, gunakan itu. Jika tidak, _id sudah cukup karena ObjectId berisi timestamp
        query = articles_collection.find({}, projection)
        
        # Sort berdasarkan published_date descending (artikel terbaru = published_date terbaru)
        # Fallback ke _id jika published_date sama atau tidak ada
        query = query.sort([('published_date', -1), ('_id', -1)])
        
        # Apply limit jika ada
        if limit:
            query = query.limit(limit)
            
        articles = list(query)
        print(f"Found {len(articles)} articles")
        
        if not articles:
            print("No articles found in database")
            return jsonify({'message': 'Tidak ada artikel ditemukan'}), 404
        
        # Convert ObjectId to string
        for article in articles:
            article['_id'] = str(article['_id'])
        
        print("Articles list request successful")
        return jsonify(articles), 200
        
    except Exception as e:
        print(f"Articles error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500

# Endpoint untuk detail artikel berdasarkan ID
@article_bp.route('/article/<article_id>', methods=['GET'])
@require_api_key
def get_article_detail(article_id):
    try:
        print(f"Processing article detail request for ID: {article_id}")
        
        # Validasi ObjectId
        if not ObjectId.is_valid(article_id):
            print("ERROR: Invalid article ID format")
            return jsonify({'message': 'ID artikel tidak valid'}), 400
        
        # Ambil semua kolom kecuali _id
        projection = {
            '_id': 0,
            'title': 1,
            'content': 1,
            'image_url': 1,
            'month_year': 1
        }
        
        article = articles_collection.find_one({'_id': ObjectId(article_id)}, projection)
        
        if not article:
            print(f"ERROR: Article not found for ID: {article_id}")
            return jsonify({'message': 'Artikel tidak ditemukan'}), 404
        
        print("Article detail request successful")
        return jsonify(article), 200
        
    except Exception as e:
        print(f"Article detail error: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Terjadi kesalahan server'}), 500
    

#Endpoint untuk Visualisasi
@article_bp.route("/api/visualization", methods=["GET"])
@require_api_key
def get_visualization_data():
    try:
        summary = visualization_collection.find_one({"_id": "summary"}, {"_id": 0})
        
        if not summary:
            return jsonify({"message": "No summary found"}), 404
        
        print(summary["data"])
        return jsonify(summary["data"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500