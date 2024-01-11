from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, current_app
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)
mongo = PyMongo()
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    mongo.init_app(current_app)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')

# Logout
@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

