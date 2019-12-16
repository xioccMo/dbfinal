from flask import Blueprint
from flask import request
from gtmd.app import db
from gtmd.models.User import User

shutdown_bp = Blueprint('shutdown_bp', '')


@shutdown_bp.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return "shutdown"
