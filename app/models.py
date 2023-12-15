from mongoengine import Document, StringField

class User(Document):
    username = StringField(required=True, max_length=50)
    email = StringField(required=True, max_length=120)
    # Add more fields as needed

#Add more models