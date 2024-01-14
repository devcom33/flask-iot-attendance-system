from flask import Flask
from flask_bootstrap import Bootstrap
from views.auth import auth_bp
from views.dashboard import dashboard_bp
from views.students import students_bp
from views.set_data import set_data_bp
from views.attend import attend_bp
from flask_pymongo import PyMongo
import os
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb+srv://mouadelbouchraoui:mouad2020@cluster0.zwdkrzd.mongodb.net/presents?retryWrites=true&w=majority'
app.config['ATLAS_API_URL'] = "https://eu-west-2.aws.data.mongodb-api.com/app/data-kraxz/endpoint/data/v1"
app.config['DATABASE_NAME'] = "presents"
app.config['COLLECTION_NAME'] = "students"
app.config['HEADERS'] = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'Lc5wESMcHqt62o43fjGBgqakGM8WWYKdLFdf4AqCD9wYsjjC6WqX58L8xi8ZwTTB',
}
UPLOAD_FOLDER = os.path.join('static/assets/', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(students_bp)
app.register_blueprint(set_data_bp)
app.register_blueprint(attend_bp)
if __name__ == '__main__':
    app.run(debug=True)