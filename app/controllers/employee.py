from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict

@app.route('/employee', methods=['GET', 'POST'])
def employee():
	if request.method == 'GET':
		return "in progress"

	if request.method == 'POST':

		data_employee = request.get_json(force=True)

		new_user = User(data_employee['email'], "chicken123", data_employee['role'])
		db.session.add(new_user)
		db.session.flush()
		db.session.refresh(new_user)

		employee_created = {"emai":data_employee['email'], "password":"chicken123","role":data_employee['role'],
			"id":new_user.id, "name":data_employee['first_name'] + " " + data_employee['last_name'],
			"department":data_employee['department'], "designation":data_employee['designation']}

		del data_employee['email']
		del data_employee['role']


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