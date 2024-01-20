from flask import Blueprint, render_template, session, redirect, url_for, current_app, Response
import requests
from flask_login import login_required
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from bson import json_util
from calendar import day_name,month_name
from dateutil.relativedelta import relativedelta

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

def get_line_chart_data():
    # start_date = datetime.strptime("2022-01-18", "%Y-%m-%d")
    # end_date = datetime.strptime("2022-01-24", "%Y-%m-%d") + relativedelta(days=1)
    pipeline = [

        {
            "$project": {
                "month": {"$month": {"$dateFromString": {"dateString": "$attendance_time"}}},
                "tag_id": 1
            }
        },
        {
            "$group": {
                "_id": "$month",
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
            "pipeline": pipeline
        }
    )
    
    if response.status_code == 200:
        documents = response.json().get('documents', [])
        print("mooooonth***************  ",documents)
        chart_data = {
            "labels": [month_name[i][:3] for i in range(12)],
            "values": [0] * 12
        }

        for d in documents:
            month_index = d["_id"]
            chart_data["values"][month_index] = d["count"]
        return chart_data
    else:
        return []
def get_bar_chart_data():
    # start_date = datetime.strptime("2022-01-18", "%Y-%m-%d")
    # end_date = datetime.strptime("2022-01-24", "%Y-%m-%d") + relativedelta(days=1)
    pipeline = [

        {
            "$project": {
                "day_of_week": {"$dayOfWeek": {"$dateFromString": {"dateString": "$attendance_time"}}},
                "tag_id": 1
            }
        },
        {
            "$group": {
                "_id": "$day_of_week",
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
            "pipeline": pipeline
        }
    )
    
    if response.status_code == 200:
        documents = response.json().get('documents', [])
        chart_data = {
            "labels": [day_name[i] for i in range(7)],
            "values": [0] * 7
        }

        for d in documents:
            day_index = d["_id"] - 2
            chart_data["values"][day_index] = d["count"]
        return chart_data
    else:
        return []
def get_top_attended():
    #all tag_id in attendance
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    pipeline = [
        {
            "$match": {
                "attendance_time": {
                    "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        },
        {
            "$sort": {"attendance_time": 1}  # Sort by attendance_time in ascending order
        },
        {
            "$limit": 5  # Limit to the top 5 records
        }
    ]
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": "attendance",
            "dataSource": "Cluster0",
            "pipeline": pipeline
        }
    )
    if response.status_code != 200:
        return []
    attendance_records = response.json().get('documents', {})

    tag_ids = [record['tag_id'] for record in attendance_records]
    if tag_ids:
        response_tags = requests.post(
            f"{ATLAS_API_URL}/action/find",
            headers=headers,
            json={
                "database": database_name,
                "collection": "students",
                "dataSource": "Cluster0",
                "filter":{"tag_id":{"$in":tag_ids}}
            }
        )
        if response_tags.status_code == 200:
            top_attendance_names = response_tags.json().get('documents', {})
            # top_attendance_names = [record.get('user_name') for record in top_attendance_names]
            return top_attendance_names
    return []
def attendance(database_name, collection_name):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    pipeline = [
        {
            "$match": {
                "attendance_time": {
                    "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    ]
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
            "pipeline": pipeline
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
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    pipeline = [
        {
            "$match": {
                "attendance_time": {
                    "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        },
        {
            "$project": {
                "hour": {"$hour": {"$dateFromString": {"dateString": "$attendance_time"}}},
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
            "pipeline": pipeline
        }
    )
    if response.status_code == 200:
        return Convert_to_arr( response.json().get('documents', {}) )
    else:
        return []

def get_presents_today():
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
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
            "pipeline" : [
                {
                    "$match": {
                        "attendance_time": {
                            "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                            "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "totalCount": {"$sum": 1}
                    }
                }
            ]
        }
    )

    if response.status_code == 200:
        count = response.json()['documents'][0]['totalCount'] if response.json()['documents'] else 0
        return count
    else:
        # Handle the error (you can log it or raise an exception)
        print(f"Error fetching data for {collection_name}. Status code: {response.status_code}")
        return 0
"""convert_date_format - is a function that converts the time format of a datetime to another format"""
def convert_date_format(input_string, input_format='%Y-%m-%d %H:%M:%S', output_format='%Y-%m-%dT%H:%M:00.000Z'):
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
        count_present_students = get_presents_today()
        attends_students = attendance(database_name, 'attendance')
        print("Ohoyaaaaaaaaaaaaaaaaaaaaaaa", extractHours(attends_students))
        
        month_data = get_line_chart_data()
        top_attended = get_top_attended()
        print("TOOOOOOOOOOOOOOOOOP: ",top_attended)
        return render_template('dashboard.html', count_students=count_students, count_presents=count_present_students, count_absent=(count_students-count_present_students), attends_students = extractHours(attends_students) ,countByTime=classify_attends(), chartData=get_bar_chart_data(), monthData=month_data, top_attended=top_attended)
    
    return redirect(url_for('auth.login'))

def attended_students():
    #all tag_id in attendance
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    pipeline = [
        {
            "$match": {
                "attendance_time": {
                    "$gte": today_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "$lt": today_end.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        }
    ]
    response = requests.post(
        f"{ATLAS_API_URL}/action/aggregate",
        headers=headers,
        json={
            "database": database_name,
            "collection": "attendance",
            "dataSource": "Cluster0",
            "pipeline": pipeline
        }
    )
    if response.status_code != 200:
        return []
    attendance_records = response.json().get('documents', {})

    tag_ids = [record['tag_id'] for record in attendance_records]
    if tag_ids:
        response_tags = requests.post(
            f"{ATLAS_API_URL}/action/find",
            headers=headers,
            json={
                "database": database_name,
                "collection": "students",
                "dataSource": "Cluster0",
                "filter":{"tag_id":{"$in":tag_ids}}
            }
        )
        if response_tags.status_code == 200:
            attendance_names = response_tags.json().get('documents', {})
            attendance_names = [record.get('user_name') for record in attendance_names]
            return attendance_names
    return []

@dashboard_bp.route('/attends/report')
def report():
    data = attended_students()
    pdf_bytes = generate_pdf(data)

    # Send the PDF as a response
    response = Response(pdf_bytes, content_type='application/pdf')
    response.headers['Content-Disposition'] = 'inline; filename=exported_list.pdf'
    return response
def generate_pdf(data_list, faculty_name="Faculté des Sciences Appliquées Ait Melloul"):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    table_data = [
        ["Attended Students:"]
    ]

    # Add attended students in a single column
    table_data.extend([["- " + item] for item in data_list])

    # Create the table and set style
    table = Table(table_data, colWidths=300, rowHeights=30)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Build the PDF document
    pdf.build([table])

    buffer.seek(0)
    return buffer.read()