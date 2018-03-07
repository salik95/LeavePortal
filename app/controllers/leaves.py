from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.utilfunc import *
from sqlalchemy import asc, and_

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
		leave_list = []
		for leave_item in leave:
			temp_dict = {}
			for item in key:
				temp_dict[item] = getattr(leave_item, item)
			leave_list.append(temp_dict)
		return jsonify(leave_list)
	else:
		return error_response_handler("Unauthorized access", 401)

@app.route('/leave_all', methods=['GET'])
def leave_all():
	leave = Balance_sheet.query.filter(Balance_sheet.emp_id == current_user.employee.id).order_by(asc(Balance_sheet.from_date))
	key = Balance_sheet.__mapper__.columns.keys()
	leave_list = []
	for leave_item in leave:
		temp_dict = {}
		for item in key:
			temp_dict[item] = getattr(leave_item, item)
		leave_list.append(temp_dict)
	return jsonify(leave_list)

@app.route('/request_all', methods=['GET'])
def request_all():
	
	key = Balance_sheet.__mapper__.columns.keys()
	pending_request_list = []
	request_history_list = []
	
	if current_user.role == "HR Manager":
		pending_requests = Balance_sheet.query.filter(Balance_sheet.hr_approval == None).order_by(asc(Balance_sheet.from_date))
		request_history = Balance_sheet.query.order_by(asc(Balance_sheet.from_date)).all()
		
		if pending_requests is not None:
			for leave_item in pending_requests:
				temp_dict = {}
				for item in key:
					temp_dict[item] = getattr(leave_item, item)
				pending_request_list.append(temp_dict)
		if request_history is not None:
			for leave_item in request_history:
				temp_dict = {}
				for item in key:
					temp_dict[item] = getattr(leave_item, item)
				request_history_list.append(temp_dict)
	else:
		pending_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(and_(Employees.reporting_manager_id == current_user.employee.id, Balance_sheet.manager_approval == None)).order_by(asc(Balance_sheet.from_date))
		request_history = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(Employees.reporting_manager_id == current_user.employee.id).order_by(asc(Balance_sheet.from_date))

		if pending_requests is not None:
			for leave_item in pending_requests:
				temp_dict = {}
				for item in key:
					temp_dict[item] = getattr(leave_item.Balance_sheet, item)
				pending_request_list.append(temp_dict)

		if request_history is not None:
			for leave_item in request_history:
				temp_dict = {}
				for item in key:
					temp_dict[item] = getattr(leave_item.Balance_sheet, item)
				request_history_list.append(temp_dict)

	request = [pending_request_list, request_history_list]
	return jsonify(request)

@app.route('/respond_request', methods=['PUT'])
def respond_request():
	response = request.get_json(force=True)
	if current_user.role == "HR Manager":
		if 'id' not in response or 'hr_remark' not in response or 'hr_approval' not in response:
			return error_response_handler("Incomplete Data", 400)
		leave = Balance_sheet.query.get(response['id'])
	else:
		if 'id' not in response or 'manager_remark' not in response or 'manager_approval' not in response:
			return error_response_handler("Incomplete Data", 400)
		leave = Balance_sheet.query.get(response['id'])
		employee_manager = Employees.query.get(leave.emp_id)
		if current_user.employee.id != employee_manager.reporting_manager_id:
			return error_response_handler("Unauthorized request", 401)

	key = list(response.keys())
	for item in key:
		setattr(leave, item, response[item])
	db.session.commit()
	db.session.flush()
	del response['id']
	return jsonify(response)