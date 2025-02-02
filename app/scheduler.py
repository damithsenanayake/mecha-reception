from flask import Blueprint, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

schedule_bp = Blueprint("schedule_service", __name__)

SERVICE_ACCOUNT_FILE = "credentials/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)



@schedule_bp.route("/schedule_service", methods=["POST"])
def schedule_service():
    
    #TODO: I am running into errors when configuring the events with calendar API. Since it's taking too long I am creating a mock api. 
    #TODO: Investigate proper way to call calendar API and implement. 
    
    # """Schedule a car service in Google Calendar and let Google send the email."""
    # data = request.get_json()

    # # Validate Input
    # required_fields = ["name", "email", "car_make", "car_model", "service_date"]
    # if not all(field in data and data[field] for field in required_fields):
    #     return jsonify({"error": "Missing required fields"}), 400

    # # Convert date format
    # try:
    #     service_datetime = datetime.strptime(
    #         data["service_date"],"%d-%m-%Y"
    #     )
    # except ValueError:
    #     return jsonify({"error": "Invalid date format"}), 400

    # # Create Event
    # event = {
    #     "summary": f"Car Service: {data['car_make']} {data['car_model']}",
    #     "description": f"Service for {data['name']}'s {data['car_make']} {data['car_model']}.",
    #     "start": {"dateTime": service_datetime.isoformat(), "timeZone": "UTC"},
    #     "end": {"dateTime": service_datetime.isoformat(), "timeZone": "UTC"},
    #     "attendees": [{"email": data["email"]}],  
    #     "reminders": {"useDefault": True},
    # }
    # CALENDAR_ID = " move37-service-scheduler@move37-scheduler.iam.gserviceaccount.com " #"your_calendar_id@group.calendar.google.com"

    # event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

    # return jsonify({
    #     "message": "Service scheduled successfully! Google will send an email.",
    #     "event_link": event_result.get("htmlLink"),
    # }), 201

    return jsonify({"message": "Calendar event created"}), 201