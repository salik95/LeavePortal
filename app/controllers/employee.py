from app.models import *
from app import db , app
from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *
from app.resources.util_functions import *
from werkzeug import check_password_hash, generate_password_hash
import string, random
from app.resources.notifications import notify

@app.route('/employee', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def employee():
	if request.method == 'GET':
		return jsonify(employee_sqlalchemy_to_list(Employees.query.all()))

	if request.method == 'POST':

		data_employee = request.get_json(force=True)

		#Refactor this thing
		#=============================
		data_employee['role'] = "Employee"
		data_employee['probation'] = 1

		password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

		new_user = User(data_employee['email'], generate_password_hash(password), data_employee['role'])
		try:
			db.session.add(new_user)
			db.session.flush()
			db.session.refresh(new_user)
		except:
			db.session.rollback()
			return redirect(url_for('dashboard'))


		employee_created = {"email":data_employee['email'],"role":data_employee['role'],
			"id":new_user.id, "name":data_employee['first_name'] + " " + data_employee['last_name'],
			"department":data_employee['department'], "designation":data_employee['designation']}

		del data_employee['email']


		data_employee['general_leaves_availed'] = '0'
		data_employee['medical_leaves_availed'] = '0'
		
		data_employee['general_leaves_remaining'] = int(settings_to_dict()['probation_leaves_limit'])
		data_employee['medical_leaves_remaining'] = int(settings_to_dict()['medical_leaves_limit'])
		data_employee['last_updated'] = data_employee['date_of_joining']
		data_employee['first_year'] = True if is_first_year(fiscal_year= settings_to_dict()['fiscal_year_starting'],\
						                  			doj=data_employee['date_of_joining'] ,\
						                   			probation_period=int(settings_to_dict()['probation_period'])) == 1 else False
		data_employee['user_id'] = new_user.id

		new_employee = Employees()
		key = list(data_employee.keys())
		for item in key:
			setattr(new_employee, item, data_employee[item])

		try:
			db.session.add(new_employee)
			db.session.commit()
			db.session.refresh(new_employee)
		except:
			db.session.rollback()
			return redirect(url_for('dashboard'))

		notify(subject='Welcome To HOH Leave Portal', body=password, receiver_id=new_employee.id)
		return jsonify(employee_created)

	if request.method == 'PUT':

		update_employee = request.get_json(force=True)
		if 'id' not in update_employee:
			return error_response_handler("Bad Request: No User ID found", 400)

		employee_data = Employees.query.get(update_employee['id'])

		key = list(update_employee.keys())
		for item in key:
			setattr(employee_data, item, update_employee[item])
		try:
			db.session.commit()
			db.session.refresh(employee_data)
		except:
			db.session.rollback()
			return redirect(url_for('dashboard'))

		new_employee = {}
		for item in Employees.__mapper__.columns.keys():
			new_employee[item] = getattr(employee_data, item)
		
		return jsonify(new_employee)

	#Refactor this delete request
	#========================================
	if request.method == 'DELETE':
		employee_credential = request.get_json(force=True)
		if 'id' in employee_credential and 'email' in employee_credential and 'password' in employee_credential:
			if current_user.employee.user.role == "HR Manager":
				emp_data = Employees.query.get(employee_credential['id'])
				emp_user_data = User.query.get(emp_data.user_id)
				if emp_user_data.email == employee_credential['email'] and check_password_hash(emp_user_data.password, employee_credential['password']):
					for leave in Balance_sheet.query.filter(Balance_sheet.emp_id == employee_credential['id']):
						db.session.delete(leave)
					db.session.commit()
					del_emp_data = {"Name":emp_data.first_name+" "+emp_data.last_name, "email":emp_user_data.email,
						"Joining Date":emp_data.date_of_joining}
					db.session.delete(emp_data)
					db.session.delete(emp_user_data)

				else:
					return error_response_handler("Forbidden: Not allowed to delete", 403)
			else:
				return error_response_handler("Forbidden: Not allowed to delete", 403)

			exists = db.session.query(db.exists().where(Employees.id == employee_credential['id'])).scalar()
			db.session.commit()
			if exists == False:
				return jsonify(del_emp_data)
			else:
				return error_response_handler("User Not Deleted", 503)
		else:
			return error_response_handler("User Credentials not provided", 404)

@app.route('/employee/search/', methods=['GET'])
@login_required
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

@app.route('/employee/<user_id>', methods=['GET'])
@login_required
def current_employee(user_id):
	employee = Employees.query.get(user_id)
	if int(current_user.employee.id) != int(user_id):
		return error_response_handler("Forbidden: Not allowed", 403)
	emp_data = {}
	for item in Employees.__mapper__.columns.keys():
		emp_data[item] = getattr(employee, item)
	emp_data['email'] = current_user.email
	return jsonify(emp_data)

@app.route('/employee/edit', methods=['GET', 'POST'])
@login_required
@is_hq_admin
def employee_update():
	
	if request.method == 'GET':

		arg_id = request.args.get("id")
		if arg_id is not None and arg_id != "":
			user_id = arg_id
			employee = Employees.query.get(user_id)
			return render_template("employee.html", data = {'employee': employee})
		else:
			flash(u"Employee Not Found", "error")
			return redirect(url_for('dashboard'))

	if request.method == 'POST':
		emp_data = request.get_json(force=True)
		if 'id' not in emp_data:
			flash(u"Something went wrong, please try again!", "error")
			return redirect('/employee/edit?id='+emp_data['id'])

		employee = Employees.query.get(emp_data['id'])
		if employee is None:
			flash(u"Something went wrong, please try again!", "error")
			return redirect('/employee/edit?id='+emp_data['id'])

		key = list(emp_data.keys())
		for item in key:
			setattr(employee, item, emp_data[item])
		try:
			db.session.commit()
			db.session.refresh(employee)
		except:
			db.session.rollback()
			return redirect(url_for('dashboard'))

		flash(u"Employee Updated Successfully", "success")
		return redirect('/employee/edit?id='+emp_data['id'])

@app.route('/account', methods=['POST', 'GET'])
@login_required
def update_account():
	if request.method == 'POST':
		flash_data = {}
		user_data = request.form.copy()
		if 'new_password' in user_data:
			flash_data.update({'for': 'form-password'})
			if not check_password_hash(current_user.password, user_data['current_password']):
				flash_data.update({'text': 'The current password you entered is incorrect.'})
				flash(flash_data, 'error')
				return redirect(url_for('update_account'))
			setattr(current_user, 'password', generate_password_hash(user_data['new_password']))
			flash_data.update({'text': 'Your password is successfully updated.'})
			flash(flash_data, 'success')

		if 'email' in user_data:
			flash_data.update({'for': 'form-email'})
			setattr(current_user, 'email', user_data['email'])
			flash_data.update({'text': 'Your email is successfully updated.'})
			flash(flash_data, 'success')

		try:
			db.session.commit()
		except:
			db.session.rollback()

		return redirect(url_for('update_account'))

	if request.method == 'GET':
		return render_template('account.html')

def employee_sqlalchemy_to_list(alchemyObject):
	col_names = Employees.__mapper__.columns.keys()
	employee_all = []
	for value in alchemyObject:
		temp_dict = {}
		for item in col_names:
			temp_dict[item] = getattr(value, item)
		employee_all.append(temp_dict)
	return employee_all