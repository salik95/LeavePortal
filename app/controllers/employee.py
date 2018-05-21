from app.models import *
from app import db , app
from flask import request, jsonify, render_template, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from sqlalchemy import func
from app.controllers.utilfunc import *
from app.resources.util_functions import *
from werkzeug import check_password_hash, generate_password_hash
import string, random
from app.resources.notifications import notify
import csv
import zipfile
import os
from flask import send_file

@app.route('/employee', methods=['GET', 'POST', 'PUT'])
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
			"department_id": data_employee['department_id'], "designation": data_employee['designation']}

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
			print(item)
			setattr(new_employee, item, data_employee[item])

		try:
			db.session.add(new_employee)
			db.session.commit()
			db.session.refresh(new_employee)
		except:
			db.session.rollback()
			return redirect(url_for('dashboard'))

		notify(subject='Welcome To HOH Leave Portal', body=password, receiver_id=new_user.id)
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

@app.route('/employee/search/', methods=['GET'])
@login_required
def employee_search():
	arg_keyword = request.args.get("keyword")
	arg_thin = request.args.get("thin")

	if arg_keyword is not None and arg_keyword != "":
		arg_keyword = arg_keyword
		employee_data = Employees.query.filter(or_(Employees.first_name.contains(arg_keyword),
			Employees.last_name.contains(arg_keyword), (func.replace(Employees.first_name+Employees.last_name, ' ', '')) == arg_keyword.replace(" ", "")))
		print(arg_keyword)

		filtered_employee = employee_sqlalchemy_to_list(employee_data)
	else:
		filtered_employee = employee_sqlalchemy_to_list(Employees.query.all())

	if arg_thin is not None:
		temp_list = []
		for emp_dict in filtered_employee:
			if emp_dict['last_name'] is None:
				temp_list.append({"id" : emp_dict['id'], "name" : emp_dict['first_name'], "designation" : emp_dict['designation']})	
			else:
				temp_list.append({"id" : emp_dict['id'], "name" : emp_dict['first_name'] + " " + emp_dict['last_name'], "designation" : emp_dict['designation']})
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
			manager = 0
			if db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(Employees.reporting_manager_id == user_id).count() > 0:
				manager = 1
			return render_template("employee.html", data = {'employee': employee})
		else:
			return render_template("employee.html")

	if request.method == 'POST':

		arg_inactive = request.args.get("inactive")
		arg_id = request.args.get("id")
		
		if arg_id is None or arg_id == "":
			flash(u"Something went wrong, please try again!", "error")
			return redirect('/employee/edit?id='+emp_data['id'])

		if arg_inactive == "true":
			try:
				employee = Employees.query.get(arg_id)

				name = employee.first_name + " " + employee.last_name

				outfile = open('app/resources/csvfiles/Balance_sheet.csv', 'w')
				outcsv = csv.writer(outfile)
				outcsv.writerow([column.name for column in Balance_sheet.__mapper__.columns])
				[outcsv.writerow([getattr(curr, column.name) for column in Balance_sheet.__mapper__.columns]) for curr in employee.balance_sheet]
				outfile.close()

				outfile = open('app/resources/csvfiles/Encashment.csv', 'w')
				outcsv = csv.writer(outfile)
				outcsv.writerow([column.name for column in Encashment.__mapper__.columns])
				[outcsv.writerow([getattr(curr, column.name) for column in Encashment.__mapper__.columns]) for curr in employee.encashment]
				outfile.close()

				for leave in employee.balance_sheet:
					db.session.delete(leave)
				db.session.commit()
				
				for encashment in employee.encashment:
					db.session.delete(encashment)
				db.session.commit()

				subordinates = Employees.query.filter(Employees.reporting_manager_id == employee.id).all()
				if subordinates is not None:
					for emp in subordinates:
						emp.reporting_manager_id = employee.reporting_manager_id
					db.session.commit()
				
				user = User.query.get(employee.user_id)
				
				db.session.delete(employee)
				db.session.delete(user)
				db.session.commit()
				
				exists = db.session.query(db.exists().where(Employees.id == arg_id)).scalar()
				if exists == False:
					flash(u"User deleted successfully!", "success")
					zipf = zipfile.ZipFile('app/resources/zipfile/Name.zip','w', zipfile.ZIP_DEFLATED)
					for root,dirs, files in os.walk('app/resources/csvfiles/'):
						for file in files:
							zipf.write('app/resources/csvfiles/'+file, os.path.basename(file))
					zipf.close()
					return send_file('resources/zipfile/Name.zip', mimetype = 'zip', attachment_filename = name + '.zip', as_attachment = True)
				else:
					flash(u"User not deleted!", "error")
					return jsonify("Failure")
			except:
				db.session.rollback()
				flash(u"Something went wrong, please try again!", "error")
				return redirect('/employee/edit?id='+arg_id)

		emp_data = request.form.copy()
		emp_data['id'] = arg_id

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

		flash(u"Employee profile is successfully updated.", "success")
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