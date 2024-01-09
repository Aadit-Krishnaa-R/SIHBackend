from app.admin import admin_bp
from flask import render_template, request, jsonify, session, redirect, url_for
from ...sentimentAnalysis.dHexagonSentimentAnalysis import dHexagonAnalysis
import os
from app.config import MONGO_URI, DB_NAME
from flask_pymongo import PyMongo
from app.models import Admin, Employee, Call
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from pymongo import MongoClient
import base64
from flask import current_app
import asyncio
import binascii
import wave
import pandas as pd
from io import BytesIO, StringIO
import io


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
    new_admin = Admin(username=username, password=hashed_password,organisation=organisation)

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
        session['admin'] = {'username': username} 
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
    admin_id = Admin.get_admin_id_by_username(admin_username)


    if admin:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        employee_usernames = Admin.get_employee_usernames(admin_id)
        if(username in employee_usernames):
            return jsonify({"message":"Employee already exists"})


        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_employee = Employee(username=username, password=hashed_password, adminid=str(admin['_id']))

        new_employee.save()

        return jsonify({"message": "Employee added successfully"}), 201
    else:
        return jsonify({"error": "Admin not found"}), 404

@admin_bp.route('/employee_det', methods=['GET'])
def get_employee_dets():
    emp_id = request.args.get('id')
    if not emp_id:
        return jsonify({'error': 'Employee ID parameter is required'}), 400

    emp = Employee.get_employee_by_id(emp_id)
    employee_username = Employee.get_username_by_id(emp_id)

    if not emp:
        return jsonify({'message': 'Employee doesn\'t exist'}), 404

    pos_percent = Call.get_positive_percent(employee_username)
    neg_percent = Call.get_neg_percent(employee_username)
    total_calls = Call.get_calls_of_calls(employee_username)
    rating = Call.get_average_rating_by_employee_name(employee_username)

    return jsonify({
        'emp_name': emp['username'],
        'emp_rating': round(rating,2),
        'emp_pos_percent': round(pos_percent, 2),
        'emp_neg_percent': round(neg_percent, 2),
        'total_calls': total_calls
    })


@admin_bp.route('/dashboard',methods=['GET'])
def top_employees_route():
    if 'admin' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)

    if admin:
        employee_usernames = Admin.get_employee_usernames(admin_id)
        employee_ratings = []
        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)
            if calls:
                average_rating = round(sum(float(call['rating']) for call in calls) / len(calls),2)
                positive_rating = round(sum(float(str(call['pos_percent']).replace('%', '')) for call in calls) / len(calls), 2)
                num_calls = len(calls)
                employee_ratings.append({'employee_name': employee_name, 'average_rating': average_rating, 'positive_rating': positive_rating, 'num_calls':num_calls})
            else:
                 employee_ratings.append({
                    'employee_name': employee_name,
                    'average_rating': 0,
                    'positive_rating': 0,
                    'num_calls': 0
                })
                

        sorted_employees = sorted(employee_ratings, key=lambda x: x['average_rating'], reverse=True)

        top_3_employees = sorted_employees[:3]

        employee_usernames = Admin.get_employee_usernames(admin_id)

        total_positive_percent = 0
        total_negative_percent = 0
        total_neutral_percent = 0

        total_calls = 0

        calls_today = 0
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)
            for call in calls:
                total_positive_percent += float(str(call['pos_percent']).replace('%', ''))
                total_negative_percent += float(str(call['neg_percent']).replace('%', ''))
                total_neutral_percent += 100 - (float(str(call['pos_percent']).replace('%', '')) + float(str(call['neg_percent']).replace('%', '')))
                total_calls += 1
                call_date = call['created_at']
                if call_date >= today_start:
                    calls_today += 1

        
        num_employees = len(employee_usernames)
        if total_calls > 0:
            average_positive_percent = round(total_positive_percent / total_calls,2)
            average_negative_percent = round(total_negative_percent / total_calls,2)
            average_neutral_percent = round(total_neutral_percent / total_calls,2)
        else:
            average_positive_percent = 0
            average_negative_percent = 0
            average_neutral_percent = 0

        response_data2 = {
            'admin_id': admin_id,
            'average_positive_percent': average_positive_percent,
            'average_negative_percent': average_negative_percent,
            'average_neutral_percent': average_neutral_percent,
            'num_calls_today': calls_today,
            'num_employees': num_employees
        }
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
        employee_usernames = Admin.get_employee_usernames(admin_id)

        employee_ratings = []

        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)
            emp_id=Employee.get_employee_id_by_username(employee_name)

            total_rating = 0
            num_calls = 0

            for call in calls:
                total_rating += float(call['rating'])
                num_calls += 1

            average_rating = total_rating / num_calls if num_calls > 0 else 0
            average_rating = average_rating

            employee_ratings.append({
                'employee_name': employee_name,
                'average_rating': average_rating,
                'num_calls':num_calls,
                'employee_id':emp_id
            })

        response_data = {
            'admin_id': admin_id,
            'employee_ratings': employee_ratings
            
        }

        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Admin not found"}), 404


@admin_bp.route('/callhistory', methods=['GET'])
def callhistory():
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)
    
    if admin:
        employee_usernames = Admin.get_employee_usernames(admin_id)
        all_calls = []
        total_call_count = 0
        total_call_count_by_employee = {}

        for employee_name in employee_usernames:
            calls = Call.get_calls_by_employee_name1(employee_name)
            call_count = len(calls)
            
            calls = [{'_id': str(call['_id']), 'duration': call['duration'],'graph_coords':call['graph_coords'],'rating':call['rating'],'pos_percent':call['pos_percent'],'neg_percent':call['neg_percent'],'employeename':call['employeename']} for call in calls]
            all_calls.extend(calls)

            total_call_count_by_employee[employee_name] = call_count
            total_call_count += call_count
        response_data = {
            'all_calls': all_calls,
            'total_call_count': total_call_count,
            'total_call_count_by_employee': total_call_count_by_employee
        }
        return jsonify(response_data)

    return jsonify({'error': 'Admin not found'}), 404


@admin_bp.route('/audio_upload', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            save_path = os.path.join(dirname, "mlaudio.wav")
            request.files['music_file'].save(save_path)
            result = dHexagonAnalysis(save_path)
            if result=="spam":
                return jsonify({"message": "spam"}), 201
            else:
                username = request.form.get('username')
                result['employeename'] = username
                result['created_at']=datetime.utcnow()
                call_collection = db['calls']
                print(">>>>>>>",result)
                call_collection.insert_one(result)
                return jsonify({"message": "Audio Upload Successful"}), 201
        except Exception as e:
            print(">>>>>>",str(e))
            return jsonify({"error": str(e)}), 500

@admin_bp.route('/input/voice', methods=['POST'])
def voice_input():
    try:
        voice_request = request.get_json()
        audio_file = voice_request.get("base64")
        audio_file=audio_file[22:]
        padding = len(audio_file) % 4
        if padding > 0:
            audio_file += '=' * (4 - padding)
        decode_string = base64.b64decode(audio_file)
        audio_path = os.path.join(dirname, "audiofrombase64.wav")
        pcm_wav_data = convert_blob_to_pcm_wav(decode_string)
        with open(audio_path, "wb") as wav_file:
             wav_file.write(pcm_wav_data)
        return jsonify({"message": "Audio Converted"}), 201

    except binascii.Error as e:
        return jsonify({"error": "Incorrect padding in base64 string", "details": str(e)}), 400

    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/input/voice_upload', methods=['POST'])
def voice_upload():
    try:
        audio_path = os.path.join(dirname, "audiofrombase64.wav")
        result = dHexagonAnalysis(audio_path)
        if result=="spam":
            return jsonify({"message": "spam"}), 201
        else:        
            result['employeename'] = "test"
            result['created_at']=datetime.utcnow()
            call_collection = db['calls']
            new_call=call_collection.insert_one(result)
            call_id=str(new_call.inserted_id)

            return jsonify({"message": "Audio Upload Successful","call_id": call_id }), 201
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500
    
        

@admin_bp.route('/issues/<days1>', methods=['GET'])
def last_seven_issues(days1):
    user_info = session.get('admin')
    if user_info:
        admin_username = user_info['username']
        admin = Admin.get_admin_by_username(admin_username)
        admin_id = Admin.get_admin_id_by_username(admin_username)
    
    if admin:
        current_date = datetime.utcnow()
        seven_days_ago = current_date - timedelta(days=int(days1))
        employee_usernames = Admin.get_employee_usernames(admin_id)
        issue_frequency = {}
        for employee_id in employee_usernames:
            employee_calls_last_7_days = Call.get_calls_by_employee_name(
                employeename=employee_id, start_date=seven_days_ago, end_date=current_date
            )
            for call in employee_calls_last_7_days:
                issues = call['issue_list']

                for issue in issues:
                    if issue in issue_frequency:
                        issue_frequency[issue] += 1
                    else:
                        issue_frequency[issue] = 1
        result_list = [{'label': issue, 'value': frequency} for issue, frequency in issue_frequency.items()]
        return jsonify({'issues_frequency': result_list})




def convert_blob_to_pcm_wav(blob):
    with wave.open(io.BytesIO(blob), 'rb') as wave_file:
        if wave_file.getsampwidth() != 2 or wave_file.getcomptype() != 'NONE':
            pcm_data = wave_file.readframes(wave_file.getnframes())
            pcm_wave = wave.open(io.BytesIO(), 'wb')
            pcm_wave.setnchannels(wave_file.getnchannels())
            pcm_wave.setsampwidth(2)  
            pcm_wave.setframerate(wave_file.getframerate())
            pcm_wave.setnframes(wave_file.getnframes())
            pcm_wave.setcomptype('NONE', 'not compressed')
            pcm_wave.writeframes(pcm_data)
            pcm_wave.seek(0)
            return pcm_wave.readframes(pcm_wave.getnframes())
        return blob
    
# @admin_bp.route('/bulkupload', methods=['POST'])
# def bulk_upload():
#     # if 'files' not in request.files:
#     #     return jsonify({'error': 'No files provided'}), 400

#     files = request.files.getlist('files')

#     uploaded_files = []

#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             uploaded_files.append(file_path)

#     return jsonify({'message': 'Files uploaded successfully', 'files': uploaded_files}


    # except Exception as e:
    #     print(f'Error during conversion: {e}')
    #     return jsonify({'error': 'Conversion failed'}), 500