from flask import Blueprint, render_template, request,current_app,url_for, session, redirect
from datetime import datetime
import requests

set_data_bp = Blueprint('set_data', __name__)
@set_data_bp.route('/set-data', methods=['GET', 'POST'])
def set_data():
    if 'username' in session:
        ATLAS_API_URL = current_app.config['ATLAS_API_URL']
        database_name = current_app.config['DATABASE_NAME']
        collection_name = current_app.config['COLLECTION_NAME']
        headers = current_app.config['HEADERS']
        if request.method == 'POST' and request.form.get('student_id') and request.form.get('name'):
            # Process the form data and store it in MongoDB Atlas
            student_id = request.form.get('student_id')
            name = request.form.get('name')
            # Add more fields as needed

            # Simulate RFID tag data
            tag_data = "672276220"

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
                    "student_id": student_id,
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
    return redirect(url_for('auth.login'))