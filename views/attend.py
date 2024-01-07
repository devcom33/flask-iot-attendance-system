from flask import Blueprint, render_template, request, current_app
from datetime import datetime
import requests

attend_bp = Blueprint('attend', __name__)
@attend_bp.route('/attend', methods = ['GET', 'POST'])
def attend():
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
    if request.method == 'POST':
        # Process the form data and store it in MongoDB Atlas
        tag_id = request.form.get('tag_data')
        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Payload for MongoDB API request (insert)
        insert_payload = {
            "dataSource": "Cluster0",
            "database": database_name,
            "collection": "attendance",
            "document": {
                "tag_id": tag_id,
                "attendance_time": current_time,
            }
        }

        # Insert attendance record
        insert_response = requests.post(
            f"{ATLAS_API_URL}/action/insertOne",
            headers=headers,
            json=insert_payload
        )

        if insert_response.status_code == 201:
            inserted_id = insert_response.json().get("insertedId")
            print("Inserted document ID:", inserted_id)
            print("RFID Tag Data:", tag_id)

            return render_template('attend.html')
        else:
            return f"Error recording attendance: {insert_response.status_code}, {insert_response.text}"
    return render_template('attend.html')