from flask import render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from app.employee import employee_bp
from run import app
mongo = PyMongo(app)


@employee_bp.route('/')
def employee_dashboard():
    # Employee dashboard logic goes here
    return {"HI":"BRO"}
#Add all employee logic

@employee_bp.route('/employee_signup', methods=['POST'])
def emp_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if mongo.db.employees.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = {'username': username, 'password': hashed_password}
    mongo.db.employees.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201






@employee_bp.route('/employee_login', methods=['POST'])
def emp_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    employee = mongo.db.employees.find_one({'username': username})

    if employee and check_password_hash(employee['password'], password):
        
        session['employee'] = {'username': username}
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401




@employee_bp.route('/employee_logout')
def emp_logout():
    
    session.pop('employee', None)
    return jsonify({'message': 'Logout successful'}), 200



@employee_bp.route('/employee_profile')
def emp_profile():
    
    if 'employee' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    
    user_info = session['employee']
    return jsonify({'username': user_info['username']}), 200
