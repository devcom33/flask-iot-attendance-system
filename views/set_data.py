from flask import Blueprint, render_template, request
from datetime import datetime
import requests

set_data_bp = Blueprint('set_data', __name__)
@set_data_bp.route('/set-data', methods=['GET', 'POST'])
def set_data():
    if request.method == 'POST':
        # Process the form data and store it in MongoDB Atlas
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        # Add more fields as needed

        # Simulate RFID tag data
        tag_data = "987654321"

        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Payload for MongoDB API request (insert)
        insert_payload = {
            "dataSource": "Cluster0",
            "database": database_name,
            "collection": collection_name,
            "document": {
                "tag_data": tag_data,
                "user_name": name,
                "employee_id": employee_id,
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
            print("Successfully recorded attendance for user:", name)
            print("Inserted document ID:", inserted_id)
            print("RFID Tag Data:", tag_data)

            return render_template('set_data.html')
        else:
            return f"Error recording attendance: {insert_response.status_code}, {insert_response.text}"

    # Render the form page for GET requests
    return render_template('set_data.html')