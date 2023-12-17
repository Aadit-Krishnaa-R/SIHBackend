from flask import Blueprint, jsonify,request
from app.models import Employee,Call
from app.employee import employee_bp


@employee_bp.route('/create',methods=['POST'])
def employee_dashboard():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    adminid = data.get('adminid')
    new_user = Employee(username=username,password=password,adminid=adminid)
    new_user.save()
    return jsonify({"message": "User created successfully"}), 201


@employee_bp.route('/all_details',methods=['GET'])
def employee_rating():
    all_calls_of_employee = Call.get_calls_by_employee_id("")
    rating_sum=0
    for call in all_calls_of_employee:
        rating_sum += call.rating
    avg_rating = rating_sum/len(all_calls_of_employee)
    return jsonify({"employee_username":"session_come_here","employee_avg_rating": avg_rating}), 201


