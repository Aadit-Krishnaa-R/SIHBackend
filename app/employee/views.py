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
        session['admin_name'] = {'username': adminUsername}


        session['access_level']=ACCESS['employee']
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@employee_bp.route('/logout')
def emp_logout():
    session.pop('employee', None)
    return jsonify({'message': 'Logout successful'}), 200

# @employee_bp.before_request
# def check_employee_login():
#     print("asksdfaisf")
#     excluded_routes = ['emp_login', 'emp_signup']
#     if request.endpoint and 'employee' not in session and request.endpoint not in excluded_routes:
#         return jsonify({'message': 'Not logged in'}), 401

@employee_bp.route('/profile')
def emp_profile():
    if 'employee' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    user_info = session['employee']
    admin_info=session['admin_name']
    return jsonify({'username': user_info['username'],
                    'admin':admin_info['username']
                    }), 200

@employee_bp.route('/call_details/<id>', methods=['GET'])
def get_calldet(id):
    call_id = id
    print(call_id)

    if not call_id:
        return jsonify({'error': 'Call ID parameter is required'}), 400

    call = Call.get_call_by_id(call_id)

    if not call:
        return jsonify({'message': 'Call not found'}), 404

    emp_name = call['employeename']
    emp_rating = Call.get_average_rating_by_employee_name(emp_name)

    return jsonify({
        'call_id': call_id,
        'duration': round(float(call['duration']),2),
        'employee_name': emp_name,
        'emp_rating': emp_rating,
        'graph_coords':call['graph_coords'],
        'rating':call['rating'],
        'emotions' : call['emotions'],
        'pos_percentage' : call['pos_percent'],
        'neg_percentage' : call['neg_percent'],
        'transcript' : call['transcript'],
        'issues' : call['issue_list'],
        'emotions_audio': call['emotions_audio']
    })

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
    
    employee_calls_count_today = Call.get_no_of_calls_by_employee_name(employee_username, start_date, end_date)
    employee_calls = Call.get_calls_by_employee_name(employee_username, start_date, end_date)
    employee_calls_count=Call.get_calls_of_calls(employee_username)
    employee_calls_all=Call.get_calls_all(employee_username)
    serialized_employee_calls = [
        {**call, '_id': str(call['_id'])} for call in employee_calls
    ]
    serialized_employee_calls2 = [
        {**call, '_id': str(call['_id'])} for call in employee_calls_all
    ]

    return jsonify({
        'employee_calls_count': employee_calls_count_today,
        'employee_calls': serialized_employee_calls2,
        'employee_total_call_count':employee_calls_count
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
    
    if (Call.get_calls_of_calls(employee_username) == 0):
        pos_percent = 0
        neg_percent = 0
        neutral_percent = 0
    else:
        pos_percent = Call.get_positive_percent(employee_username)
        neg_percent = Call.get_neg_percent(employee_username)
        neutral_percent = 100 - pos_percent - neg_percent

    return jsonify({
        'positive_percent': round(pos_percent,2),
        'negative_percent': round(neg_percent,2),
        'neutral_percent': round(neutral_percent,2)
    })
