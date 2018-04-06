from flask import jsonify, make_response
from flask_login import current_user

def error_response_handler(message, errno=404):
	return make_response(jsonify({"message": message}), errno)

def is_hq_admin(f):
	def wrapper(*args, **kwargs):
		if current_user.role == 'HR Manager':
			return f(*args, **kwargs)
		else:
			return error_response_handler("User Not Authroized", 403)
	return wrapper