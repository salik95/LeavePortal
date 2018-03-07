from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.utilfunc import *
from sqlalchemy import asc

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

#Revisit this fucntionality
#=======================================================
@app.route('/leave_all/super', methods=['GET'])
def leave_all_super():
	if current_user.role == 'HR Manager' or current_user.role == 'General Manager':
		leave = Balance_sheet.query.order_by(asc(Balance_sheet.from_date)).all()
		key = Balance_sheet.__mapper__.columns.keys()
		my_list = []
		for leave_item in leave:
			my_dict = {}
			for item in key:
				my_dict[item] = getattr(leave_item, item)
			my_list.append(my_dict)
		return jsonify(my_list)
	else:
		return error_response_handler("Unauthorized access", 401)