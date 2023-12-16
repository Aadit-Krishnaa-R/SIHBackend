from flask import Blueprint, jsonify,request
from app.models import get_db,User
from app.employee import employee_bp

from datetime import datetime


#sample route to use the database
#add all employee routes here
@employee_bp.route('/')
def employee_dashboard():
    # print("Hi")
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    new_user = User(username=username, email=email)

    # Save the User object to the 'users' collection
    new_user.save()

    return jsonify({"message": "User created successfully"}), 201
