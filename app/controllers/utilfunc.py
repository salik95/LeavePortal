from flask import jsonify, make_response

def error_response_handler(message, errno=404):
	return make_response(jsonify({"message": message}), errno)