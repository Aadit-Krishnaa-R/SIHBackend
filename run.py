from app import create_app
from flask_cors import CORS
from flask import Response, request

if __name__ == '__main__':
    app = create_app()
    CORS(app, resources={r"/*":{"origins":["http://localhost:3000", "http://localhost:5000","http://192.168.179.244:5000","http://192.168.179.35:3000"]}}, supports_credentials=True)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run()
