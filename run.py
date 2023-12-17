from app import create_app

#dont touch this file too

if __name__ == '__main__':
    app = create_app()

    app.run(debug=True,port=8080)




# app = create_app()
# app.config['MONGO_URI'] = 'mongodb+srv://aaditkrishnaa18:hkALbbvCNLh1gQsg@sih.l0g5uni.mongodb.net/?retryWrites=true&w=majority'