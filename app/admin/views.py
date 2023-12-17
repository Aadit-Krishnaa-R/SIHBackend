from flask import render_template,request,jsonify
from app.admin import admin_bp
from ..sentimentAnalysis.main import main
import os
from app.config import MONGO_URI, DB_NAME
from pymongo import MongoClient


client = MongoClient(MONGO_URI)
db = client[DB_NAME]


dirname = os.path.dirname(__file__)
#add all admin routes



@admin_bp.route('/audio_upload', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            save_path = os.path.join(dirname, "mlaudio.wav")
            request.files['music_file'].save(save_path)
            result = main(save_path)
            username = request.form.get('username')
            result['employeUsername'] = username
            call_collection = db['calls']
            call_collection.insert_one(result)
            print(result)
            return jsonify(result),201
        except Exception as e:
            return jsonify({"error": str(e)}), 500