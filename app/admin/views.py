from app.admin import admin_bp
from flask import render_template, request, jsonify, session, redirect, url_for
from ..sentimentAnalysis.myModel import main
import os
from app.config import MONGO_URI, DB_NAME
from flask_pymongo import PyMongo
from app.models import Admin, Employee, Call
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pymongo import MongoClient
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
dirname = os.path.dirname(__file__)

ACCESS={
    'admin':'0',
    'employee':"1"
}

@admin_bp.route('/admin_signup', methods=['POST'])
def adm_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    organisation=data.get('organisation')
    confirm_pwd=data.get('confirm_pwd')

    if not username or not password or not organisation or not confirm_pwd:
        return jsonify({'message': 'Username and password are required'}), 400
    if confirm_pwd != password:
        return jsonify({'message':'Password is not matching'}), 400

    if Admin.get_admin_by_username(username):
        return jsonify({'message': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_admin = Admin(username=username, password=hashed_password)

    new_admin.save()

    return jsonify({'message': 'User registered successfully'}), 201


@admin_bp.route('/admin_login', methods=['POST'])
def adm_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = Admin.get_admin_by_username(username)

    if admin and check_password_hash(admin['password'], password):
        session['access_level']=ACCESS['admin']
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
    

@admin_bp.route('/admin_logout', methods=['GET'])
def adm_logout():
    session.pop('admin', None)
    return jsonify({'message': 'Logout successful'}), 200


@admin_bp.route('/admin_profile')
def adm_profile():
    if 'admin' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_info = session['admin']
    return jsonify({'username': user_info['username']}), 200


@admin_bp.route('/add_employee',methods=['POST'])
def add_emp():
    user_info=session['admin']
    admin_username = user_info['username']
    admin = Admin.get_admin_by_username(admin_username)

    if admin:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        # Create an Employee object with the admin_id

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_employee = Employee(username=username, password=hashed_password, adminid=str(admin['_id']))

        # Save the Employee object to the 'employee' collection
        new_employee.save()

        return jsonify({"message": "Employee added successfully"}), 201
    else:
        return jsonify({"error": "Admin not found"}), 404



@admin_bp.route('/add_call',methods=['POST'])
def add_call():
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)

        if admin:
            data = request.get_json()

            graph_coords = data.get('graph_coords')
            emotions = data.get('emotions')
            pos_percent = data.get('pos_percent')
            neg_percent = data.get('neg_percent')
            rating = data.get('rating')
            language = data.get('language')
            duration = data.get('duration')
            gender = data.get('gender')
            employee_name = data.get('employee_name')

            employee = Employee.get_employee_by_username(employee_name)

            if employee:
                # Create a Call object
                new_call = Call(
                    graph_coords=graph_coords,
                    emotions=emotions,
                    pos_percent=pos_percent,
                    neg_percent=neg_percent,
                    rating=rating,
                    language=language,
                    duration=duration,
                    gender=gender,
                    employeename=employee_name  # Use employee name instead of ID
                )
                new_call.save()

                return jsonify({"message": f"Call added successfully for employee {employee_name}"}), 201
            else:
                return jsonify({"error": "Employee not found"}), 404
        else:
            return jsonify({"error": "Admin not found"}), 404
    else:
        return jsonify({"error": "User not authenticated"}), 401



@admin_bp.route('/dashboard',methods=['GET'])
def top_employees_route():
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)


    # db = get_db()
    # admin = Admin.get_admin_by_id(admin_id)

    if admin:
        # Retrieve the usernames of all employees associated with the admin
        employee_usernames = Admin.get_employee_usernames(admin_id)

        # Calculate the average rating for each employee
        employee_ratings = []
        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)
            if calls:
                # Calculate the average rating
                average_rating = round(sum(float(call['rating']) for call in calls) / len(calls),2)
                positive_rating = round(sum(float(call['pos_percent'].rstrip('%')) for call in calls)/len(calls),2)
                num_calls = len(calls)
                employee_ratings.append({'employee_name': employee_name, 'average_rating': average_rating, 'positive_rating': positive_rating, 'num_calls':num_calls})
            else:
                # If there are no calls, set the average rating to 0
                # employee_ratings.append({'employee_name': employee_name, 'average_rating': 0})
                 employee_ratings.append({
                    'employee_name': employee_name,
                    'average_rating': 0,
                    'positive_rating': 0,
                    'num_calls': 0
                })
                

        # Sort employees by average rating in descending order
        sorted_employees = sorted(employee_ratings, key=lambda x: x['average_rating'], reverse=True)

        # Take the top 3 employees
        top_3_employees = sorted_employees[:3]

        employee_usernames = Admin.get_employee_usernames(admin_id)

        # Initialize variables to store cumulative percentages
        total_positive_percent = 0
        total_negative_percent = 0
        total_neutral_percent = 0

        # Count the number of calls for calculating averages
        total_calls = 0

        #counting the number of calls today

        calls_today = 0
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)

            for call in calls:
                total_positive_percent += float(call['pos_percent'].rstrip('%'))
                total_negative_percent += float(call['neg_percent'].rstrip('%'))
                total_neutral_percent += 100 - (float(call['pos_percent'].rstrip('%')) + float(call['neg_percent'].rstrip('%')))
                total_calls += 1


                call_date = call['created_at']
                if call_date >= today_start:
                    calls_today += 1

        
        num_employees = len(employee_usernames)
        # Calculate average percentages
        if total_calls > 0:
            average_positive_percent = round(total_positive_percent / total_calls,2)
            average_negative_percent = round(total_negative_percent / total_calls,2)
            average_neutral_percent = round(total_neutral_percent / total_calls,2)
        else:
            average_positive_percent = 0
            average_negative_percent = 0
            average_neutral_percent = 0

        # Prepare the response
        response_data2 = {
            'admin_id': admin_id,
            'average_positive_percent': average_positive_percent,
            'average_negative_percent': average_negative_percent,
            'average_neutral_percent': average_neutral_percent,
            'num_calls_today': calls_today,
            'num_employees': num_employees
        }
        # Prepare the response
        response_data = [{
            'employee_name': entry['employee_name'],
            'average_rating': entry['average_rating'],
            'positive_rating': entry['positive_rating'],
            'num_calls': entry['num_calls']
        } for entry in top_3_employees]

        return jsonify({"top_employees": response_data},{"Admin_Ratings": response_data2}), 200
    else:
        return jsonify({"error": "Admin not found"}), 404



@admin_bp.route('/employees',methods=['GET'])
def employees():
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)
    if admin:
        # Retrieve the usernames of all employees associated with the admin
        employee_usernames = Admin.get_employee_usernames(admin_id)

        # Initialize a list to store employee ratings
        employee_ratings = []

        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)

            # Calculate the average rating for the employee
            total_rating = 0
            num_calls = 0

            for call in calls:
                total_rating += float(call['rating'])
                num_calls += 1

            average_rating = total_rating / num_calls if num_calls > 0 else 0

            # Add employee and rating to the list
            employee_ratings.append({
                'employee_name': employee_name,
                'average_rating': average_rating,
                'num_calls':num_calls
            })

        # Prepare the response
        response_data = {
            'admin_id': admin_id,
            'employee_ratings': employee_ratings
        }

        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Admin not found"}), 404




@admin_bp.route('/callhistory',methods=['GET'])
def callhistory():
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)
    if admin:
        # Retrieve the usernames of all employees associated with the admin
        employee_usernames = Admin.get_employee_usernames(admin_id)

        # Initialize a list to store call history
        call_history = []

        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)

            for call in calls:
                # Add call details to the list
                call_history.append({
                    'employee_name': employee_name,
                    'call_id': str(call['_id']),
                    'call_rating': call['rating']
                })

        # Prepare the response
        response_data = {
            'admin_id': admin_id,
            'call_history': call_history
        }

        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Admin not found"}), 404


@admin_bp.route('/audio_upload', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            save_path = os.path.join(dirname, "mlaudio.wav")
            request.files['music_file'].save(save_path)
            print("main1")
            result = main(save_path)
            print("main2")
            username = request.form.get('username')
            result['employeename'] = username
            call_collection = db['calls']
            call_collection.insert_one(result)
            print(result)
            return jsonify(result),201
        except Exception as e:
            return jsonify({"error": str(e)}), 500