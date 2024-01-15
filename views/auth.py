from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, current_app,flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import requests


auth_bp = Blueprint('auth', __name__)
# mongo = PyMongo()
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    ATLAS_API_URL = current_app.config['ATLAS_API_URL']
    database_name = current_app.config['DATABASE_NAME']
    headers = current_app.config['HEADERS']

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Payload for MongoDB API request (findOne)
        find_payload = {
            "dataSource": "Cluster0",
            "database": database_name,
            "collection": "users",
            "filter": {"username": username}
        }

        # Find user in the MongoDB collection
        response = requests.post(
            f"{ATLAS_API_URL}/action/findOne",
            headers=headers,
            json=find_payload
        )

        if response.status_code == 200:
            user = response.json().get('document',{})
            print(user)
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Invalid username or password', 'error')
        else:
            flash('Error connecting to MongoDB API', 'error')

    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

