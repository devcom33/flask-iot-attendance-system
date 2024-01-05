from flask import Blueprint, render_template

attend_bp = Blueprint('attend', __name__)

@attend_bp.route('/attend')
def attend():
    return render_template('attend.html')