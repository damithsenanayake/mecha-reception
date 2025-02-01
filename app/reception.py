from flask import Blueprint, jsonify, request
import base64
import os
import tempfile
from openai import OpenAI
from configparser import ConfigParser

conf_parser = ConfigParser()

conf_parser.read('./app/config.ini') # don't push api-key ;) 

client = OpenAI(api_key= conf_parser.get('API_KEY', 'openai') )


reception = Blueprint("main", __name__)

@reception.route('/hello', methods=['GET'])
def ping():
    return jsonify({"message": "Welcome to YoCah mechanics..."}), 200


@reception.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        data = request.json
        if "audio" not in data:
            return jsonify({"error": "Missing 'audio' field"}), 400

        audio_data = base64.b64decode(data["audio"])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
    
        with open(temp_audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(model = 'whisper-1', file = audio_file)#openai.Audio.transcribe("whisper-1", audio_file)

        os.unlink(temp_audio_path)
        
        return jsonify({'transcript':response.text})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    
    
        