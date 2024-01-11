from flask import Blueprint, render_template, request, current_app, abort,url_for, session, redirect
import requests

students_bp = Blueprint('students', __name__)

@students_bp.route('/students')
def display_students():
    if 'username' in session:
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
    return redirect(url_for('auth.login'))

@students_bp.route('/students/edit/<string:student_id>',methods=['GET', 'POST'])
def update_student(student_id):
    pass
@students_bp.route('/students/view/<string:student_id>',methods=['GET'])
def view_student():
    pass
@students_bp.route('/students/delete/<string:student_id>',methods=['GET'])
def delete_student():
    pass