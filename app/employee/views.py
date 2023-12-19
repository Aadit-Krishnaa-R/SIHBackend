from flask import Blueprint, request, jsonify, session
from flask_cors import CORS, cross_origin

from flask_pymongo import PyMongo
from app.models import Employee, Call,Admin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta

from app.employee import employee_bp
from bson import ObjectId

today_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

ACCESS={
    'admin':'0',
    'employee':"1"
}

@employee_bp.route('/create',methods=['POST'])
def employee_dashboard():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    adminid = data.get('adminid')
    new_user = Employee(username=username,password=password,adminid=adminid)
    new_user.save()
    return jsonify({"message": "User created successfully"}), 201




# @employee_bp.route('/all_details',methods=['GET'])
# def employee_rating():
#     all_calls_of_employee = Call.get_calls_by_employee_id("")
#     rating_sum=0
#     for call in all_calls_of_employee:
#         rating_sum += call.rating
#     avg_rating = rating_sum/len(all_calls_of_employee)
#     return jsonify({"employee_username":"session_come_here","employee_avg_rating": avg_rating}), 201

@employee_bp.route('/signup', methods=['POST'])
def emp_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    adminid = session['adminid']

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    if Employee.get_employee_by_username(username):
        return jsonify({'message': 'Username already taken'}), 400

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
        return jsonify({'message': 'Username and password are required'}), 400
    employee = Employee.get_employee_by_username(username)
    adminid = employee['adminid']
    print(adminid)

    admin = Admin.get_admin_by_id(adminid)
    adminUsername = admin['username']
    
    if employee and check_password_hash(employee['password'], password):
        session['employee'] = {'username': username}
        session['admin'] = {'username': adminUsername}

        session['access_level']=ACCESS['employee']
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@employee_bp.route('/logout')
def emp_logout():
    session.pop('employee', None)
    return jsonify({'message': 'Logout successful'}), 200

def check_employee_login():
    excluded_routes = [ 'emp_login', 'emp_signup']  # Add any other routes you want to exclude
    if request.endpoint and 'employee' not in session and request.endpoint not in excluded_routes:
        return jsonify({'message': 'Not logged in'}), 401

@employee_bp.route('/profile')
def emp_profile():
    if 'employee' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    user_info = session['employee']
    admin_info=session['admin']
    return jsonify({'username': user_info['username'],
                    'admin':admin_info['username']
                    }), 200


@employee_bp.route('/employee_calls', methods=['GET'])
def get_employee_calls():
    emp_info=session['employee']

    employee_username = emp_info['username']

    if not employee_username:
        return jsonify({'message': 'Employee name is required in the request body'}), 400

    today_date = datetime.now().date()
    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

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
    emp_info=session['employee']
    
    employee_username = emp_info['username']

    if not employee_username:
        return jsonify({'message': 'Employee username is required in the request body'}), 400

    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    average_rating = Call.get_average_rating_by_employee_name(employee_username)

    return jsonify({'employee_rating': average_rating})


@employee_bp.route('/response_graph', methods=['GET'])
def get_response_graph():
    emp_info=session['employee']
    

    employee_username = emp_info['username']

    if not employee_username:
        return jsonify({'message': 'Employee username is required in the request body'}), 400

    employee = Employee.get_employee_by_username(employee_username)

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    pos_percent = Call.get_positive_percent(employee_username)
    neg_percent = Call.get_neg_percent(employee_username)
    neutral_percent = 100 - pos_percent - neg_percent

    return jsonify({
        'positive_percent': pos_percent,
        'negative_percent': neg_percent,
        'neutral_percent': neutral_percent
    })
