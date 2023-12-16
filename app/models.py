from pymongo import MongoClient
from datetime import datetime
from app.config import MONGO_URI, DB_NAME


client = MongoClient(MONGO_URI)
db = client[DB_NAME]

#Sample Model, Create all models like this just copy paste and edit
class User:
    def __init__(self, username, email, created_at=None):
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at
        }

    def save(self):
        # Access the 'users' collection
        users_collection = db['users']

        # Convert the User object to a dictionary
        user_data = self.to_dict()

        # Insert the user document into the 'users' collection
        users_collection.insert_one(user_data)

def get_db():
    return db







# # # # app/models.py

# # from datetime import datetime
# # # from app import mongo
# # # from flask import current_app



# # import bson

# # from flask import current_app, g
# # from werkzeug.local import LocalProxy
# # from flask_pymongo import PyMongo
# # from pymongo.errors import DuplicateKeyError, OperationFailure
# # from bson.objectid import ObjectId
# # from bson.errors import InvalidId


# # def get_db():
# #     """
# #     Configuration method to return db instance
# #     """
# #     db = getattr(g, "_database", None)

# #     if db is None:

# #         db = g._database = PyMongo(current_app).db
       
# #     return db


# # # Use LocalProxy to read the global db instance with just `db`
# # db = LocalProxy(get_db)

# # print(type(db))

# # # class User:
# # #     def __init__(self, username, email):
# # #         self.username = username
# # #         self.email = email
# # #         self.created_at = datetime.utcnow()


    
# # #     def save(self):
# # #         # Insert the user document into the "users" collection
# # #         # mongo = current_app.extensions['mongo']
# # #         # mongo = current_app.extensions.get('pymongo')
# # #         db.users.insert_one({
# # #             'username': self.username,
# # #             'email': self.email,
# # #             'created_at': self.created_at
# # #         })
# # #         print(type(db.users))

# # #     @staticmethod
# # #     def get_all():
# # #         # mongo = current_app.extensions['mongo']
# # #         # mongo = current_app.extensions.get('pymongo')
# # #         # Retrieve all users from the "users" collection
# # #         return list(db.users.find())



# from datetime import datetime
# from flask import current_app, g
# from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
# from pymongo.errors import DuplicateKeyError
# from bson.objectid import ObjectId

# def get_db():
#     db = getattr(g, "_database", None)

#     if db is None:
#         db = g._database = PyMongo(current_app).db

#     return db

# db = LocalProxy(get_db)

# class User:
#     def __init__(self, username, email):
#         self.username = username
#         self.email = email
#         self.created_at = datetime.utcnow()

#     def save(self):
#         try:
#             db.users.insert_one({
#                 'username': self.username,
#                 'email': self.email,
#                 'created_at': self.created_at
#             })
#         except DuplicateKeyError:
#             # Handle duplicate key error if needed
#             pass

#     @staticmethod
#     def get_all():
#         return list(db.users.find())



# models.py



# def create_user(username, email):
#     user = {
#         'username': username,
#         'email': email,
#         'created_at': datetime.utcnow()
#     }

#     users_collection.insert_one(user)

# def get_users():
#     users = users_collection.find()
#     users_data = [
#         {
#             'username': user['username'],
#             'email': user['email'],
#             'created_at': user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
#         }
#         for user in users
#     ]

#     return users_data