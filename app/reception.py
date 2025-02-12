from flask import Blueprint, jsonify, request, session
import base64
import os
import tempfile
from openai import OpenAI
from configparser import ConfigParser
import json
import requests

conf_parser = ConfigParser()

conf_parser.read("./app/config.ini")  # don't push api-key ;)

client = OpenAI(api_key=conf_parser.get("API_KEY", "openai"))


reception = Blueprint("main", __name__)

form = {
    "name": None,
    "email": None,
    "car_make": None,
    "car_model": None,
    "service_date": None,
    "known_issues":None,
}


def update_memory(history, input, output):
    """Simple implementation of a buffer memory

    Args:
        history (str): json string
        input (str): user input
        output (str): ai output
    """
    messages = json.loads(history)

    messages.append({"human": input, "ai": output})

    return json.dumps(messages)


def get_memory_buffer(memory_string, k=3):
    """get last k messages of the memory

    Args:
        memory_string (str): the json list string of the messages
        k (int, optional): how many last messages to send. Defaults to 3.
    """

    messages = json.loads(memory_string)[-k:]

    return "\n".join([f"human: {m['human']} \n ai: {m['ai']}" for m in messages])


def parse_for_form_fields(message, form_data):
    prompt = f"""
    The user is filling out a car service form with the following fields:
    {"\n".join([f"{i+1}. {list(form.keys())[i]}" for i in range(len(form.keys()))])}

    The following form data has been provided so far:
    {json.dumps(form_data, indent=4)}

    Based on the user's input below, extract any relevant information and provide a JSON object with the following keys:
    {f"\n -".join(list(form_data.keys()))}

    If the information is missing or not clear from the user's input, leave the field as null.
    
    Important: service_date needs to be in the 'DD-MM-YYYY' format. 
    
    User input: "{message}"

    Respond with a JSON object.
    """
    system_message = {"role": "system", "content": prompt}
    messages = [system_message, {"role": "user", "content": ""}]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
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
        response = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )

    os.unlink(temp_audio_path)

    return response.text


@reception.route("/hello", methods=["GET"])
def ping():
    return jsonify({"message": "Welcome to YoCah mechanics..."}), 200


@reception.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        data = request.json
        if "audio" not in data:
            return jsonify({"error": "Missing 'audio' field"}), 400

        return jsonify({"transcript": transcribe_b64(data["audio"])})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@reception.route("/fill_form", methods=["POST"])
def fill_json_form():

    try:
        data = request.json

        try:
            history = session["memory"]
        except:
            history = "[]"
            session["memory"] = history

        try:
            form_data = session["form"]
        except:
            form_data = form.copy()
            session["form"] = form_data
        if "audio" not in data:
            return jsonify({"error": "Missing 'audio' field"}), 400
        user_input = transcribe_b64(data["audio"])

        extracted_info = parse_for_form_fields(user_input, form_data)
        print(f"\nExtracted Info: {json.dumps(extracted_info, indent=4)}")

        for key in form_data:
            if form_data[key] is None and extracted_info.get(key):
                if extracted_info[key] is not None: 
                    form_data[key] = extracted_info[key]

        print(f"Updated Form: {json.dumps(form_data, indent=4)}")

        session['form'] = form_data
        finish_convo = is_form_complete(form_data)

        user_message = {"role": "user", "content": user_input}

        if not finish_convo:
            system_message = {
                "role": "system",
                "content": f"""You are a helpful assistant. Your goal is to extract information to fill out the missing information in follwing given form. 
                {json.dumps(form_data, indent=4)}.
                provide an appropriate response to the user so that they will provide necessary missing information.
                Be courteous and engaging. 
                If the form is complete, finish the conversation with a greeting. 
                
                Conversation Buffer: {get_memory_buffer(history)}
                
                """,
            }
        else:
            system_message = {
                "role": "system",
                "content": f"""You were carrying on a conversation to try and fill a form with a user. 
                The form is now complete. Please end the conversation with an appropriate response. 
                Chat Buffer: 
                {get_memory_buffer(history)}
                """,
            }

        messages = [system_message, user_message]

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
            )
            resp_text = response.choices[0].message.content

            history = update_memory(history, user_input, resp_text)
            aud_resp = client.audio.speech.create(
                model="tts-1", voice="alloy", input=resp_text
            )
            session['history'] = history

            audio_content = aud_resp.content

            audio_b64 = base64.b64encode(audio_content).decode("utf-8")
            if is_form_complete(form_data):
                
                schedule_response = requests.post(url="http://localhost:5000/schedule_service", json=form_data)
                
                if schedule_response.status_code == 201:
                    
                    pass
                
                else :
                    print("scheduling error")
                    #TODO: add logic to get conflicts, available times and re-engage user for preference. 
            return jsonify({"audio": audio_b64, "form_complete": finish_convo})

        except Exception as e:
            print(f"Error occurred: {e}")
    except Exception as e:

        return jsonify({"error": str(e)}), 500
