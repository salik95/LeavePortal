from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *

@app.route('/employee', methods=['GET', 'POST', 'PUT'])
def employee():
	if request.method == 'GET':
		return jsonify(employee_sqlalchemy_to_list(Employees.query.all()))

	if request.method == 'POST':

		data_employee = request.get_json(force=True)

		#Refactor this thing
		data_employee['role'] = "Employee"

		new_user = User(data_employee['email'], "hoh123", data_employee['role'])
		db.session.add(new_user)
		db.session.flush()
		db.session.refresh(new_user)


		employee_created = {"email":data_employee['email'], "password":"chicken123","role":data_employee['role'],
			"id":new_user.id, "name":data_employee['first_name'] + " " + data_employee['last_name'],
			"department":data_employee['department'], "designation":data_employee['designation']}

		del data_employee['email']


		data_employee['general_leaves_availed'] = '0'
		data_employee['medical_leaves_availed'] = '0'
		
		data_employee['general_leaves_remaining'] = int(settings_to_dict()['general_leaves_limit'])
		data_employee['medical_leaves_remaining'] = int(settings_to_dict()['medical_leaves_limit'])
		
		data_employee['user_id'] = new_user.id

		new_employee = Employees()
		key = list(data_employee.keys())
		for item in key:
			setattr(new_employee, item, data_employee[item])

		db.session.add(new_employee)
		db.session.commit()
		db.session.flush()
		return jsonify(employee_created)

	if request.method == 'PUT':

		update_employee = request.get_json(force=True)
		if 'id' not in update_employee:
			return error_response_handler("Bad Request: No User ID found", 400)

		employee_data = Employees.query.get(update_employee['id'])

		if 'password' in update_employee:
			if current_user.employee.id == update_employee['id']:
				user_data = User.query.get(employee_data.user_id)
				setattr(user_data, 'password', update_employee['password'])
			else:
				return error_response_handler("Not Allowed: User Not allowed to change password", 404)

		if 'email' in update_employee:
			if current_user.employee.id == update_employee['id']:
				user_data = User.query.get(employee_data.user_id)
				setattr(user_data, 'email', update_employee['email'])
			else:
				return error_response_handler("Not Allowed: User Not allowed to change email", 404)

		key = list(update_employee.keys())
		for item in key:
			setattr(employee_data, item, update_employee[item])
		db.session.commit()
		db.session.flush()
		db.session.refresh(employee_data)

		new_employee = {}
		for item in Employees.__mapper__.columns.keys():
			new_employee[item] = getattr(employee_data, item)
		
		return jsonify(new_employee)


@app.route('/employee/search/', methods=['GET'])
def employee_search():
	arg_keyword = request.args.get("keyword")
	arg_thin = request.args.get("thin")

	if arg_keyword is not None and arg_keyword != "":
		arg_keyword = arg_keyword + "%"
		employee_data = Employees.query.filter(or_(Employees.first_name.contains(arg_keyword),
			Employees.last_name.contains(arg_keyword)))
		filtered_employee = employee_sqlalchemy_to_list(employee_data)
	else:
		filtered_employee = employee_sqlalchemy_to_list(Employees.query.all())

	if arg_thin is not None:
		temp_list = []
		for emp_dict in filtered_employee:
			temp_list.append({"id" : emp_dict['id'], "name" : emp_dict['first_name']+" "+emp_dict['last_name'],
				"designation" : emp_dict['designation']})
		filtered_employee = temp_list

	return jsonify(filtered_employee)

def employee_sqlalchemy_to_list(alchemyObject):
	col_names = Employees.__mapper__.columns.keys()
	employee_all = []
	for value in alchemyObject:
		temp_dict = {}
		for item in col_names:
			temp_dict[item] = getattr(value, item)
		employee_all.append(temp_dict)
	return employee_all