from flask import Blueprint, render_template, request, current_app, url_for, session, redirect, flash
from datetime import datetime, timedelta
import requests

attend_bp = Blueprint('attend', __name__)

def checkTag(tag_id):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
    
    try:
        response = requests.post(
            f"{ATLAS_API_URL}/action/findOne",
            headers=headers,
            json={
                "database": database_name,
                "collection": collection_name,
                "dataSource": "Cluster0",
                "filter": {"tag_id": tag_id}
            }
        )
        response.raise_for_status()  # an exception for 4xx and 5xx status codes

        tag_id = response.json().get('document', {})
        if tag_id is None:
            return None
        return tag_id

    except requests.RequestException as e:
        flash(f"Error checking tag: {str(e)}", 'danger')
        return None
def checkExist(tag_id):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    response = requests.post(
        f"{ATLAS_API_URL}/action/findOne",
        headers=headers,
        json={
            "database": database_name,
            "collection": "attendance",
            "dataSource": "Cluster0",
            "filter": {
                "tag_id": tag_id,
                "attendance_time": {
                    "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    )

    tag_id = response.json().get('document', {})
    if tag_id is None:
        return None
    return tag_id

def recordAttendance(tag_id):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_payload = {
            "dataSource": "Cluster0",
            "database": database_name,
            "collection": "attendance",
            "document": {
                "tag_id": tag_id,
                "attendance_time": current_time,
            }
        }

        insert_response = requests.post(
            f"{ATLAS_API_URL}/action/insertOne",
            headers=headers,
            json=insert_payload
        )
        insert_response.raise_for_status()

        if insert_response.status_code == 201:
            flash('This student attended successfully.', 'success')
            return True
        else:
            flash(f"Error recording attendance: {insert_response.status_code}, {insert_response.text}", 'danger')
            return False

    except requests.RequestException as e:
        flash(f"Error recording attendance: {str(e)}", 'danger')
        return False

@attend_bp.route('/attend', methods=['GET', 'POST'])
def attend():
    if 'username' in session:
        if request.method == 'POST' and request.form.get('tag_data'):
            tag_id = request.form.get('tag_data')
            if checkExist(tag_id) is not None:
                flash('This student is Already attended', 'danger')
                return render_template('attend.html')
            student_info = checkTag(tag_id)

            if student_info is None:
                flash('No student found with this tag.', 'danger')
            else:
                if recordAttendance(tag_id):
                    return render_template('attend.html')

        return render_template('attend.html')

    return redirect(url_for('auth.login'))
