from flask import Flask, render_template, request, redirect, url_for, current_app, abort
import requests
from datetime import datetime
from flask_bootstrap import Bootstrap
from views.home import home_bp
from views.dashboard import dashboard_bp
from views.students import students_bp
from views.set_data import set_data_bp
from views.attend import attend_bp

app = Flask(__name__)
bootstrap = Bootstrap(app)

# MongoDB Atlas Data API configuration
app.config['ATLAS_API_URL'] = "https://eu-west-2.aws.data.mongodb-api.com/app/data-kraxz/endpoint/data/v1"
app.config['DATABASE_NAME'] = "presents"
app.config['COLLECTION_NAME'] = "students"
app.config['HEADERS'] = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'Lc5wESMcHqt62o43fjGBgqakGM8WWYKdLFdf4AqCD9wYsjjC6WqX58L8xi8ZwTTB',
}
app.register_blueprint(home_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(students_bp)
app.register_blueprint(set_data_bp)
app.register_blueprint(attend_bp)
if __name__ == '__main__':
    app.run(debug=True)