from mongoengine import Document, StringField

class User(Document):
    username = StringField(required=True, max_length=50)
    email = StringField(required=True, max_length=120)
    # Add more fields as needed

#Add more models

calls_schema={
    
        "callid": int,
        "empid": int,
        "adminid": int,
        "coordinates": {
            "x": float,
            "y": float
        },
        "emotions": {
            "neutral":bool,
            "gratitude":bool,

            "happy": bool,
            "sad": bool,
            "anger": bool
        },
        "pos_percent": float,
        "neg_percent": float,
        "rating": int,
        "language": str,
        "duration": int
    
}


emp_schema = {
    "empid": int,
    "username": str,
    "password": str
}


admin_schema = {
    "adminid": int,
    "username": str,
    "password": str,
}