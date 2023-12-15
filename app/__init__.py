from flask import Flask
from flask_mongoengine import MongoEngine
from config import Config
from app.admin import admin_bp
from app.employee import employee_bp

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine(app)

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(employee_bp, url_prefix='/employee')
