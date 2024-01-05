from flask import Blueprint, render_template, request, current_app, abort
import requests

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
def display_students():
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
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
        student_data = response.json().get('documents', [])
        return render_template('students.html', data=student_data)
    else:
        return f"Error fetching attendance data. Status code: {response.status_code}"

def update_student():
    pass
def delete_student():
    pass