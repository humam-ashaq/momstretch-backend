from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

uri = os.getenv("DB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['momstretch']

users_collection = db['users']
articles_collection = db['articles']
visualization_collection = db['visualization']
history_collection = db['login_history']
movement_collection = db['movement']
stretching_collection = db['stretching']
epds_collection = db['epds_records']
stretch_history_collection = db['stretch_history']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)