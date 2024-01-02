from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

# MongoDB Atlas Data API configuration
ATLAS_API_URL = "https://eu-west-2.aws.data.mongodb-api.com/app/data-kraxz/endpoint/data/v1"
database_name = "presents"
collection_name = "students"
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'Lc5wESMcHqt62o43fjGBgqakGM8WWYKdLFdf4AqCD9wYsjjC6WqX58L8xi8ZwTTB',
}

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
            "pipeline":[{ "$group": {"_id": None, "totalCount": { "$sum": 1 }}}]
        }
    )
    if response.status_code == 200:
        count_students = response.json()
        count_students = count_students['documents'][0]['totalCount']
        return render_template('dashboard.html', cnt=count_students)
    else:
        print(f"Error fetching attendance data. Status code: {response.status_code}")
    return render_template('dashboard.html')
@app.route('/attendance')
def display_attendance():
    # Fetch attendance data from MongoDB Atlas
    response = requests.post(
        f"{ATLAS_API_URL}/action/find",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
        }
    )
    if response.status_code == 200:
        attendance_data = response.json().get('documents', [])
        print(attendance_data)
        return render_template('attendance.html', data=attendance_data)
    else:
        return f"Error fetching attendance data. Status code: {response.status_code}"

@app.route('/set-data', methods=['GET', 'POST'])
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

            return redirect(url_for('attendance'))
        else:
            return f"Error recording attendance: {insert_response.status_code}, {insert_response.text}"

    # Render the form page for GET requests
    return render_template('set_data.html')

if __name__ == '__main__':
    app.run(debug=True)