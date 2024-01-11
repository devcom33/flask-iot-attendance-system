from flask import Blueprint, render_template, request, current_app, abort, session, redirect, url_for
import requests
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' in session:
        ATLAS_API_URL = current_app.config['ATLAS_API_URL']
        database_name = current_app.config['DATABASE_NAME']
        collection_name = current_app.config['COLLECTION_NAME']
        headers = current_app.config['HEADERS']
        students_response = requests.post(
            f"{ATLAS_API_URL}/action/aggregate",
            headers=headers,
            json={
                "database": database_name,
                "collection": collection_name,
                "dataSource": "Cluster0",
                "pipeline":[{ "$group": {"_id": None, "totalCount": { "$sum": 1 }}}]
            }
        )
        attendance_response = requests.post(
            f"{ATLAS_API_URL}/action/aggregate",
            headers=headers,
            json={
                "database": database_name,
                "collection": "attendance",
                "dataSource": "Cluster0",
                "pipeline":[{ "$group": {"_id": None, "totalCount": { "$sum": 1 }}}]
            }
        )
        if students_response.status_code == 200 and attendance_response.status_code == 200:
            count_students = students_response.json()['documents'][0]['totalCount'] if students_response.json()['documents'] else 0
            count_present_students = attendance_response.json()['documents'][0]['totalCount'] if attendance_response.json()['documents'] else 0
            return render_template('dashboard.html', count_students=count_students, count_presents=count_present_students)
        else:
            print(f"Error fetching attendance data. Status code: {response.status_code}")
        return render_template('dashboard.html')
    return redirect(url_for('auth.login'))