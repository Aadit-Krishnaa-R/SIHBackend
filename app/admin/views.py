from flask import render_template, request, jsonify, session, redirect, url_for
from app.admin import admin_bp
from run import app
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
mongo = PyMongo(app)
@admin_bp.route('/')
def admin_dashboard():
    # Admin dashboard logic 
    return {"HI":"Bro"}
#add all admin logic


@admin_bp.route('/admin_signup', methods=['POST'])
def adm_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if mongo.db.admins.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = {'username': username, 'password': hashed_password}
    mongo.db.admins.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201




@admin_bp.route('/admin_login', methods=['POST'])
def adm_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = mongo.db.admins.find_one({'username': username})

    if admin and check_password_hash(admin['password'], password):
        
        session['admin'] = {'username': username}
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401



@admin_bp.route('/admin_logout')
def adm_logout():
    
    session.pop('admin', None)
    return jsonify({'message': 'Logout successful'}), 200

@admin_bp.route('/admin_profile')
def adm_profile():
    
    if 'admin' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    
    user_info = session['admin']
    return jsonify({'username': user_info['username']}), 200
