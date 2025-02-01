from flask import Blueprint, jsonify, request, session
import base64
import os
import tempfile
from openai import OpenAI
from configparser import ConfigParser
import json
from langchain.memory import ConversationBufferMemory

conf_parser = ConfigParser()

conf_parser.read('./app/config.ini') # don't push api-key ;) 

client = OpenAI(api_key= conf_parser.get('API_KEY', 'openai') )


reception = Blueprint("main", __name__)

form = {
    'name': None,
    'email': None,
    'car_make': None,
    'car_model': None,
    'date_of_service': None
}

def parse_for_form_fields(message, form_data):
    prompt = f"""
    The user is filling out a car service form with the following fields:
    {"\n".join([f"{i+1}. {list(form.keys())[i]}" for i in range(len(form.keys()))])}

    The following form data has been provided so far:
    {json.dumps(form_data, indent=4)}

    Based on the user's input below, extract any relevant information and provide a JSON object with the following keys:
    {f"\n -".join(list(form.keys()))}

    If the information is missing or not clear from the user's input, leave the field as null.

    User input: "{message}"

    Respond with a JSON object.
    """
    system_message = {
        "role": "system",
        "content": prompt
    }
    messages=[system_message, {"role":"user", "content":""}]

    response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=messages,
        )

    try:
        response_text = response.choices[0].message.content.strip()
        parsed_json = json.loads(response_text)
        return parsed_json
    except json.JSONDecodeError:
        print("Error parsing JSON. Returning empty data.")
        return {}
    
def is_form_complete(form):
    return all(value is not None for value in form.values())

def transcribe_b64(b64_audio):
    
        audio_data = base64.b64decode(b64_audio)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name
    
        with open(temp_audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(model = 'whisper-1', file = audio_file)
        
        os.unlink(temp_audio_path)
  
        return response.text


@reception.route('/hello', methods=['GET'])
def ping():
    return jsonify({"message": "Welcome to YoCah mechanics..."}), 200


@reception.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        data = request.json
        if "audio" not in data:
            return jsonify({"error": "Missing 'audio' field"}), 400
        
        return jsonify({'transcript':transcribe_b64(data["audio"])})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    
@reception.route("/fill_form", methods=["POST"])
def fill_json_form():
    
    try:
        data = request.json
        

        try: 
            history = session['memory']
        except:
            history = ""
            session['memory'] = history

    
        
        try: 
            form_data = session['form']
        except: 
            form_data = form
            session['form'] = form_data
        if "audio" not in data:
            return jsonify({"error": "Missing 'audio' field"}), 400        
        user_input = transcribe_b64(data["audio"])
        system_message = {
            "role": "system",
            "content": f"""You are a helpful assistant. Your goal is to extract information to fill out the missing information in follwing given form. 
            {json.dumps(form_data, indent=4)}.
            provide an appropriate response to the user so that they will provide necessary missing information.
            Be courteous and engaging. 
            If the form is complete, finish the conversation with a greeting. 
            
            Conversation Buffer: {history}
            
            """
        }
        extracted_info = parse_for_form_fields(user_input, form_data)
        print(f"\nExtracted Info: {json.dumps(extracted_info, indent=4)}")

        for key in form_data:
            if form_data[key] is None and extracted_info.get(key):
                form_data[key] = extracted_info[key]

        print(f"Updated Form: {json.dumps(form_data, indent=4)}")
        user_message = {
            "role": "user",
            "content": user_input
        }
        messages = [system_message, user_message]

        try:
            response = client.chat.completions.create(
                model="gpt-4",  
                messages=messages,
            )
            resp_text = response.choices[0].message.content
            
            history += f"""
            
            human: {user_input}
            ai: {resp_text}
            
            """
            aud_resp =  client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=resp_text
            )
            
            audio_content = aud_resp.content

            audio_b64 = base64.b64encode(audio_content).decode('utf-8')
            
            return jsonify({'audio':audio_b64, 'form_complete':is_form_complete(form_data)})
                  
        
        except Exception as e:
            print(f"Error occurred: {e}")
    except Exception as e:
        
        return jsonify({"error": str(e)}), 500
        
        