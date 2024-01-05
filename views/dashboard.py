from flask import Blueprint, render_template, request, current_app, abort
import requests

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    collection_name = current_app.config['COLLECTION_NAME']
    headers = current_app.config['HEADERS']
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