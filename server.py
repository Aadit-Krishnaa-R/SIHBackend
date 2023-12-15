from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import base64
from io import BytesIO
import wave
import dHexagonSentimentAnalysis as dHex


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calls.db'  # SQLite database for simplicity
db = SQLAlchemy(app)


Eid=1000


# Define your SQLAlchemy model for storing call information
class Call(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    graph_coordinates = db.Column(db.String(255))
    caller_emotions = db.Column(db.String(255))
    call_pos_percent = db.Column(db.Float)
    call_neg_percent = db.Column(db.Float)
    call_rating = db.Column(db.Float)
    call_language = db.Column(db.String(50))
    call_duration = db.Column(db.Float)
    caller_gender = db.Column(db.String(50))
# db.create_all()
# Sample route for handling audio file upload and processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    # Assuming the audio file is sent as form data with key 'audio_file'
    # audio_file = request.files['audio_file']

    data = request.get_json()
    audio_base64 = data['audio_base64']

    # Decode base64 to get binary audio data
    audio_binary = base64.b64decode(audio_base64)

    # Save the binary audio data to a .wav file
    wav_filename = 'audio_file.wav'
    with open(wav_filename, 'wb') as wav_file:
        wav_file.write(audio_binary)

    result=dHex.dHexagonAnalysis('./audio_file.wav')




    # Perform inference with your ML model and get the outputs
    # Replace the following lines with your actual ML model inference code
    Eid+=1
    graph_coordinates = result.coordinates
    caller_emotions = result.emotions
    call_pos_percent = result.pos_percent
    call_neg_percent = result.neg_percent
    call_rating = result.rating
    call_language = result.language
    call_duration = result.duration
    caller_gender = result.duration

    # Save results to the database
    call = Call(
        id=Eid,
        graph_coordinates=str(graph_coordinates),
        caller_emotions=str(caller_emotions),
        call_pos_percent=call_pos_percent,
        call_neg_percent=call_neg_percent,
        call_rating=call_rating,
        call_language=call_language,
        call_duration=call_duration,
        caller_gender=caller_gender
    )
    db.session.add(call)
    db.session.commit()

    # Return the results as JSON
    result = {
        'graph_coordinates': graph_coordinates,
        'caller_emotions': caller_emotions,
        'call_pos_percent': call_pos_percent,
        'call_neg_percent': call_neg_percent,
        'call_rating': call_rating,
        'call_language': call_language,
        'call_duration': call_duration,
        'caller_gender': caller_gender
    }
    return jsonify(result)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
