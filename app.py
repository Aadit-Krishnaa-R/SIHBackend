from flask import Flask, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from admin_model import admin_schema
from emp_model import emp_schema

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'  
app.config['MONGO_URI'] = "mongodb+srv://saranya:AkPTsUoyHXkAqTxD@sih.l0g5uni.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)

@app.route('/admin_signup', methods=['POST'])
def adm_signup():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if mongo.db.admins.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = {'username': username, 'password': hashed_password}
    mongo.db.admins.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/employee_signup', methods=['POST'])
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

@app.route('/admin_login', methods=['POST'])
def adm_login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = mongo.db.admins.find_one({'username': username})

    if admin and check_password_hash(admin['password'], password):
        
        session['admin'] = {'username': username}
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/employee_login', methods=['POST'])
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


@app.route('/admin_logout')
def adm_logout():
    
    session.pop('admin', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/employee_logout')
def emp_logout():
    
    session.pop('employee', None)
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/admin_profile')
def adm_profile():
    
    if 'admin' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    
    user_info = session['admin']
    return jsonify({'username': user_info['username']}), 200


@app.route('/employee_profile')
def emp_profile():
    
    if 'employee' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    
    user_info = session['employee']
    return jsonify({'username': user_info['username']}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)
