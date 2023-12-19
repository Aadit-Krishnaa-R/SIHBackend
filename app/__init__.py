# from flask import Flask
# from flask_pymongo import PyMongo
# from app.admin import admin_bp
# from app.employee import employee_bp

# def create_app():
#     app = Flask(__name__)
#     app.secret_key='secret_key'
#     app.register_blueprint(admin_bp, url_prefix='/admin')
#     app.register_blueprint(employee_bp, url_prefix='/employee')

#     return app

from flask import Flask
from flask_pymongo import PyMongo
from app.admin import admin_bp
from app.employee import employee_bp
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.secret_key='sdnsjsjfbwfiwf'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    return app