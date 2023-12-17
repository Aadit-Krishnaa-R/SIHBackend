from flask import Blueprint, request, jsonify, session
from flask_pymongo import PyMongo
from app.models import Employee, Call
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta
from app.employee import employee_bp
from bson import ObjectId

today_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

ACCESS={
    'admin':'0',
    'employee':"1"

}

@employee_bp.route('/signup', methods=['POST'])
def emp_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    adminid = data.get('adminid')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    if Employee.get_employee_by_username(username):
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_employee = Employee(username=username, password=hashed_password, adminid=adminid)

    new_employee.save()

    return jsonify({'message': 'User registered successfully'}), 201

@employee_bp.route('/login', methods=['POST'])
def emp_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    
    employee = Employee.get_employee_by_username(username)

    if employee and check_password_hash(employee['password'], password):
        session['employee'] = {'username': username}
        session['access_level']=ACCESS['employee']
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@employee_bp.route('/logout')
def emp_logout():
    session.pop('employee', None)
    return jsonify({'message': 'Logout successful'}), 200

@employee_bp.route('/profile')
def emp_profile():
    if 'employee' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_info = session['employee']
    return jsonify({'username': user_info['username']}), 200


@employee_bp.route('/employee_calls', methods=['GET'])
def get_employee_calls():
    data = request.get_json()

    employee_username = data.get('employee_name')

    if not employee_username:
        return jsonify({'error': 'Employee name is required in the request body'}), 400

    today_date = datetime.now().date()
    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    start_date = datetime.combine(today_date, datetime.min.time())
    end_date = start_date + timedelta(days=1)
    
    employee_calls_count = Call.get_no_of_calls_by_employee_name(employee_username, start_date, end_date)
    employee_calls = Call.get_calls_by_employee_name(employee_username, start_date, end_date)
    serialized_employee_calls = [
        {**call, '_id': str(call['_id'])} for call in employee_calls
    ]

    return jsonify({
        'employee_calls_count': employee_calls_count,
        'employee_calls': serialized_employee_calls
    })


@employee_bp.route('/rating', methods=['GET'])
def get_employee_rating():
    data = request.get_json()

    employee_username = data.get('employee_username')

    if not employee_username:
        return jsonify({'error': 'Employee username is required in the request body'}), 400

    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    average_rating = Call.get_average_rating_by_employee_name(employee_username)

    return jsonify({'employee_rating': average_rating})


@employee_bp.route('/response_graph', methods=['GET'])
def get_response_graph():
    data = request.get_json()

    employee_username = data.get('employee_username')

    if not employee_username:
        return jsonify({'error': 'Employee username is required in the request body'}), 400

    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    pos_percent = Call.get_positive_percent(employee_username)
    neg_percent = Call.get_neg_percent(employee_username)
    neutral_percent = 100 - pos_percent - neg_percent

    return jsonify({
        'positive_percent': pos_percent,
        'negative_percent': neg_percent,
        'neutral_percent': neutral_percent
    })

















