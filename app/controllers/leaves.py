from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user

@app.route('/leave', methods=['GET', 'POST', 'PUT', 'DELETE'])
def leave():
	if request.method = 'GET':
		