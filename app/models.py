from pymongo import MongoClient
from datetime import datetime
from app.config import MONGO_URI, DB_NAME
from bson import ObjectId
from datetime import timedelta


client = MongoClient(MONGO_URI)
db = client[DB_NAME]

class Employee:
    def __init__(self,username,password,adminid,created_at=None):
        self.username = username
        self.password = password
        self.adminid = adminid
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'adminid': self.adminid,
            'created_at': self.created_at
        }

    def save(self):
        employee_collection = db['employee']
        employee_data = self.to_dict()
        employee_collection.insert_one(employee_data)

    def get_employee_by_id(employee_id):
        employee_collection = db['employee']
        return employee_collection.find_one({'_id': ObjectId(employee_id)})
    def get_employee_by_username(username):
        employee_collection = db['employee']
        return employee_collection.find_one({'username': username})

    def update(self, employee_id):
        employee_collection = db['employee']
        employee_collection.update_one({'_id': ObjectId(employee_id)}, {'$set': self.to_dict()})

    def delete(self, employee_id):
        employee_collection = db['employee']
        employee_collection.delete_one({'_id': ObjectId(employee_id)})

class Call:
    def __init__(self,graph_coords,emotions,pos_percent,neg_percent,rating,language,duration,gender,employeename,created_at=None):
        self.graph_coords = graph_coords
        self.emotions = emotions
        self.pos_percent =pos_percent
        self.neg_percent =neg_percent
        self.rating = rating
        self.language = language
        self.duration = duration
        self.gender = gender
        self.employeename = employeename

        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
            return {
            'graph_coords' : self.graph_coords,
            'emotions' : self.emotions,
            'pos_percent' : self.pos_percent, 
            'neg_percent' : self.neg_percent,
            'rating' : self.rating,
            'language' : self.language,
            'duration' : self.duration,
            'gender' : self.gender,
            'employeename' : self.employeename,
            'created_at': self.created_at
        }

    def save(self):
        call_collection = db['calls']
        call_data = self.to_dict()
        call_collection.insert_one(call_data)

    def get_call_by_id(call_id):
        call_collection = db['calls']
        return call_collection.find_one({'_id': ObjectId(call_id)})
    def get_no_of_calls_by_employee_name(employee_name, start_date, end_date):
        call_collection = db['calls']
        filter_criteria = {'employeename': employee_name}

        if start_date and end_date:
            filter_criteria['created_at'] = {
                '$gte': start_date,
                '$lt': end_date
        }

        employee_calls_cursor = call_collection.find(filter_criteria)
        employee_calls_count = len(list(employee_calls_cursor))

        return employee_calls_count

        
    def get_calls_by_employee_name(employeename, start_date, end_date):
        call_collection = db['calls']

        filter_criteria = {'employeename': employeename}
    
        if start_date and end_date:
            filter_criteria['created_at'] = {
                '$gte': start_date,
                '$lt': end_date
        }
        employee_calls = list(call_collection.find(filter_criteria).sort('created_at', -1))

        return employee_calls

    def get_average_rating_by_employee_name(employeename):
        call_collection = db['calls']

        filter_criteria = {'employeename': employeename}
        employee_calls = list(call_collection.find(filter_criteria))

        if not employee_calls:
            return 0  

        total_rating = 0
        for call in employee_calls:
            rating_str = call.get('rating', '0')  
            rating_str = rating_str.replace('%', '')  
            total_rating += float(rating_str)

        average_rating = total_rating / len(employee_calls)
        return average_rating 

    def get_positive_percent(employeename):
        call_collection=db['calls']
        filter_criteria={'employeename':employeename}
        employee_calls=list(call_collection.find(filter_criteria))
        if not employee_calls:
            return 0
        total_pos_percent=0
        for call in employee_calls:
            pos_percent=call.get('pos_percent',0)
            pos_percent=pos_percent.replace('%','')
            total_pos_percent+=float(pos_percent)
    
        total_pos=total_pos_percent/len(employee_calls)
        


        return total_pos


    def get_neg_percent(employeename):
        call_collection=db['calls']
        filter_criteria={'employeename':employeename}
        employee_calls=list(call_collection.find(filter_criteria))
        if not employee_calls:
            return 0
        total_neg_percent=0
        for call in employee_calls:
            neg_percent=call.get('neg_percent',0)
            neg_percent=neg_percent.replace('%','')
            total_neg_percent+=float(neg_percent)
        
        total_neg=total_neg_percent/len(employee_calls)
        

        return total_neg



        




    def update(self, call_id):
        call_collection = db['calls']
        call_collection.update_one({'_id': ObjectId(call_id)}, {'$set': self.to_dict()})

    def delete(self, call_id):
        call_collection = db['calls']
        call_collection.delete_one({'_id': ObjectId(call_id)})

class Admin:
    def __init__(self,username,password,created_at=None):
            self.username = username
            self.password = password
            self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'created_at': self.created_at
        }

    def save(self):
        admin_collection = db['admin']
        admin_data = self.to_dict()
        admin_collection.insert_one(admin_data)
    def get_admin_by_id(admin_id):
        admin_collection = db['admin']
        return admin_collection.find_one({'_id': ObjectId(admin_id)})
    
    def get_admin_by_username(username):
        admin_collection = db['admin']
        return admin_collection.find_one({'username': username})

    def update(self, admin_id):
        admin_collection = db['admin']
        admin_collection.update_one({'_id': ObjectId(admin_id)}, {'$set': self.to_dict()})

    def delete(self, admin_id):
        admin_collection = db['admin']
        admin_collection.delete_one({'_id': ObjectId(admin_id)})


    def get_db():
        return db







