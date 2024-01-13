from flask import Blueprint, render_template, request, current_app, abort,url_for, session, redirect, Response
import requests
from reportlab.pdfgen import canvas
from io import BytesIO

students_bp = Blueprint('students', __name__)
#Just A Global Variable
student_data = 0
@students_bp.route('/students')
def display_students():
    if 'username' in session:
        ATLAS_API_URL = current_app.config['ATLAS_API_URL']
        database_name = current_app.config['DATABASE_NAME']
        collection_name = current_app.config['COLLECTION_NAME']
        headers = current_app.config['HEADERS']

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
            global student_data
            student_data = response.json().get('documents', [])
            return render_template('students.html', data=student_data)
        else:
            return f"Error fetching attendance data. Status code: {response.status_code}"
    return redirect(url_for('auth.login'))

@students_bp.route('/students/edit/<string:student_id>',methods=['GET', 'POST'])
def update_student(student_id):
    pass
@students_bp.route('/students/view/<string:student_id>',methods=['GET'])
def view_student(student_id):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
    # return f"Viewing student with ID: {student_id}"
    response = requests.post(
        f"{ATLAS_API_URL}/action/findOne",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
            "filter":{"student_id": student_id}
        }
    )
    if response.status_code == 200:
        student_id = response.json().get('document', {})
        return render_template('view.html', data=student_id)
    else:
        return f"Error fetching attendance data. Status code: {response.status_code}, {student_id}"

    return "Hey"
@students_bp.route('/students/delete/<string:student_id>',methods=['GET'])
def delete_student(student_id):
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
    response = requests.post(
        f"{ATLAS_API_URL}/action/deleteOne",
        headers=headers,
        json={
            "database": database_name,
            "collection": collection_name,
            "dataSource": "Cluster0",
            "filter":{"student_id": student_id}
        }
    )
    if response.status_code == 200:
        return redirect(url_for('students.display_students'))
    else:
        return f"Error Not Deleted. Status code: {response.status_code}, {student_id}"

@students_bp.route('/students/report')
def report():
    display_students()
    data = [record.get('user_name') for record in student_data]
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
    pdf.drawString(100, 800, "Exported List:")
    
    y_position = 780
    for item in data_list:
        y_position -= 20
        pdf.drawString(120, y_position, item)

    pdf.save()
    buffer.seek(0)

    return buffer.read()