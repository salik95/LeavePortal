from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.utilfunc import *

@app.route('/leave_form', methods=['POST'])
def leave_form():
	leave_data = request.get_json(force=True)

	if 'from_date' not in leave_data or 'to_date' not in leave_data or 'purpose' not in leave_data or 'leave_type' not in leave_data:
		return error_response_handler("Incomplete Data", 400)
	
	leave_data['emp_id'] = current_user.employee.id
	new_leave = Balance_sheet()
	key = list(leave_data.keys())
	for item in key:
		setattr(new_leave, item, leave_data[item])
	db.session.add(new_leave)
	db.session.commit()
	db.session.flush()

	leave_dict = {}
	for col_name in Balance_sheet.__mapper__.columns.keys():
		leave_dict[col_name] = getattr(new_leave, col_name)
	
	return jsonify(leave_dict)