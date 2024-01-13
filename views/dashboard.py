from flask import Blueprint, render_template, session, redirect, url_for, current_app, Response
import requests
from flask_login import login_required
from datetime import datetime
from reportlab.pdfgen import canvas
from io import BytesIO

dashboard_bp = Blueprint('dashboard', __name__)

def make_api_request(database_name, collection_name):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
            "pipeline": [{ "$group": {"_id": None, "totalCount": { "$sum": 1 }}}]
        }
    )

    if response.status_code == 200:
        count = response.json()['documents'][0]['totalCount'] if response.json()['documents'] else 0
        return count
    else:
        # Handle the error (you can log it or raise an exception)
        print(f"Error fetching data for {collection_name}. Status code: {response.status_code}")
        return 0



def attendance(database_name, collection_name):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
        }
    )

    if response.status_code == 200:
        allAttends = response.json().get('documents', [])
        return allAttends
    else:
        # Handle the error (you can log it or raise an exception)
        print(f"Error fetching data for {collection_name}. Status code: {response.status_code}")
        return 0

def Convert_to_arr(counts_by_time):
    return [record.get('count') for record in counts_by_time]

def classify_attends():
    pipeline = [
        {
            "$project":{
                "hour":{"$hour": {"$dateFromString": {"dateString": "$attendance_time"}}},
                "tag_id": 1
            }
        },
        {
            "$group": {
                "_id": "$hour",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": "attendance",
            "dataSource": "Cluster0",
            "pipeline":pipeline
        }
    )
    if response.status_code == 200:
        return Convert_to_arr( response.json().get('documents', {}) )
    else:
        return "Walooooo!!!!"



"""convert_date_format - is a function that converts the time format of a datetime to another format"""
def convert_date_format(input_string, input_format='%Y-%m-%d %H:%M:%S', output_format='%Y-%m-%dT%H:00:00.000Z'):
    try:
        dt_object = datetime.strptime(input_string, input_format)
        formatted_string = dt_object.strftime(output_format)
        return formatted_string
    except ValueError:
        return None

def extractHours(attends_students):
    return [convert_date_format(record.get('attendance_time')) for record in attends_students]

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'username' in session:
        database_name = current_app.config['DATABASE_NAME']

        # Make API requests
        count_students = make_api_request(database_name, current_app.config['COLLECTION_NAME'])
        count_present_students = make_api_request(database_name, 'attendance')
        attends_students = attendance(database_name, 'attendance')
        classify_attends()
        attended_students()
        return render_template('dashboard.html', count_students=count_students, count_presents=count_present_students, count_absent=(count_students-count_present_students), attends_students = extractHours(attends_students) ,countByTime=classify_attends())
    
    return redirect(url_for('auth.login'))

def attended_students():
    #all tag_id in attendance
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/find",
        headers=headers,
        json={
            "database": database_name,
            "collection": "attendance",
            "dataSource": "Cluster0",
        }
    )
    if response.status_code == 200:
        attendance_records = response.json().get('documents', {})
        tag_ids = [record['tag_id'] for record in attendance_records]
    response_tags = requests.post(
        f"{ATLAS_API_URL}/action/find",
        headers=headers,
        json={
            "database": database_name,
            "collection": "students",
            "dataSource": "Cluster0",
            "filter":{"tag_data":{"$in":tag_ids}}
        }
    )
    if response_tags.status_code == 200 and tag_ids:
        attendance_names = response_tags.json().get('documents', {})
        attendance_names = [record.get('user_name') for record in attendance_names]
        return attendance_names

@dashboard_bp.route('/attends/report')
def report():
    data = attended_students()
    pdf_bytes = generate_pdf(data)

    # Send the PDF as a response
    response = Response(pdf_bytes, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=exported_list.pdf'
    return response
def generate_pdf(data_list):
    # Create a PDF document
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # Set up PDF content
    pdf.drawString(100, 800, "Attended Students:")
    
    y_position = 780
    for item in data_list:
        y_position -= 20
        pdf.drawString(120, y_position, item)

    pdf.save()
    buffer.seek(0)

    return buffer.read()
