from flask import Blueprint, request, jsonify, session
from flask_pymongo import PyMongo
from app.models import get_db, Employee  
from werkzeug.security import generate_password_hash, check_password_hash
from run import app
from datetime import datetime
from app.employee import employee_bp

mongo = PyMongo(app)


@employee_bp.route('/employee_signup', methods=['POST'])
def emp_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    
    new_employee = Employee(username=username, password=password, adminid=None)

    new_employee.save()

    return jsonify({'message': 'User registered successfully'}), 201

@employee_bp.route('/employee_login', methods=['POST'])
def emp_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    
    employee = Employee.get_employee_by_username(username)

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





