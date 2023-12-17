from flask import Flask
from flask_pymongo import PyMongo
from app.admin import admin_bp
from app.employee import employee_bp


#dont touch this file 



def create_app():
    app = Flask(__name__)
    app.secret_key='sdnsjsjfbwfiwf'



    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/employee')

    return app



# from app.config import Config
# from models import get_db
# import certifi
# app = Flask(__name__)

# ca = certifi.where()
# app.config.from_object(Config)

    # Register blueprints, set up routes, etc.

    # app.config.from_object(Config)
    # app.config['MONGO_URI']='mongodb+srv://aaditkrishnaa18:hkALbbvCNLh1gQsg@sih.l0g5uni.mongodb.net/?retryWrites=true&w=majority'

    # Initialize extensions
    # mongo.init_app(app)
# app.config.from_object(Config)

# mongo = PyMongo(app)

# mongo = PyMongo()
# app.register_blueprint(admin_bp, url_prefix='/admin')
# app.register_blueprint(employee_bp, url_prefix='/employee')
