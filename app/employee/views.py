from flask import Blueprint, jsonify,request
from app.models import get_db,Employee
from app.employee import employee_bp


@employee_bp.route('/',methods=['POST'])
def employee_dashboard():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    adminid = data.get('adminid')
    new_user = Employee(username=username,password=password,adminid=adminid)
    new_user.save()
    return jsonify({"message": "User created successfully"}), 201
