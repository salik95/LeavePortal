import csv
from app.models import *
from app import db , app
from flask import request, jsonify, render_template , redirect
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *
import logging 
<<<<<<< HEAD
import os
from werkzeug.utils import secure_filename
from flask import flash


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def upload_file(file):
	if file.filename == '':
	    flash('No selected file')
	    return False
	
	filename = secure_filename(file.filename)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def read_csv(link):
	with open(link) as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		list_of_elemet = []
		for index, row in enumerate(reader):
			if index == 0:
				keys = row
			else:
				list_of_elemet.append(dict(zip(keys[0].split(','), row[0].split(','))))
		return list_of_elemet

@app.route('/bulk_upload_user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_user():

	try:
		if request.method == 'GET':
			return render_template("bulk_upload.html")

		if request.method == 'POST':
			if 'file' not in request.files:
				flash('No file part')
				return redirect(request.url)
			file = request.files['file']

			if file and allowed_file(file.filename)==False:
				print('file')
				flash('No file part')
				return redirect(request.url)

			link_of_file = upload_file(request.files['file'])
			print('main',link_of_file)
			list_of_elemet = read_csv(link_of_file)

			list_of_employee_object = []
			for i in list_of_elemet:
				one_user = User(i['email'], "hoh123", i['role'])
				db.session.add(one_user)
				db.session.commit()
				del i['email'] 
				del i['role']
				i['user_id'] = one_user.id
				new_employee = Employees() 
				for item in i.keys():
					if item != 'reporting_manager_email':
						setattr(new_employee, item, i[item])
				list_of_employee_object.append(new_employee)

			db.session.add_all(list_of_employee_object)
			db.session.commit()

			list_of_employee_object = []



			for i in list_of_elemet:
				new_employee = Employees.query.filter_by(user_id=str(i['user_id'])).first()
				manager_user = User.query.filter_by(email=i['reporting_manager_email']).first()
				manager_employee = Employees.query.filter_by(user_id=str(manager_user.id)).first()
				setattr(new_employee, 'reporting_manager_id', manager_employee.id)
				db.session.commit()
				db.session.flush()
				db.session.refresh(new_employee)
=======

@app.route('/bulk_upload_user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_user():
	try:
		with open('app/controllers/temp.csv') as csvfile:
		    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		    #csv_keys = reader[0] 
		    list_of_elemet = []
		    for index, row in enumerate(reader):
		        if index == 0:
		            keys = row
		        else:
		            list_of_elemet.append(dict(zip(keys[0].split(','), row[0].split(','))))
			
		list_of_employee_object = []
		list_of_user_object = []
		#print (list_of_elemet[0])

		for i in list_of_elemet:
			one_user = User(i['email'], "hoh123", i['role'])
			db.session.add(one_user)
			db.session.commit()
			del i['email'] 
			del i['role']
			i['user_id'] = one_user.id
			new_employee = Employees() 
			for item in i.keys():
				if item != 'reporting_manager_email':
					setattr(new_employee, item, i[item])
			list_of_employee_object.append(new_employee)

		db.session.add_all(list_of_employee_object)
		db.session.commit()

		list_of_employee_object = []



		for i in list_of_elemet:
			new_employee = Employees.query.filter_by(user_id=str(i['user_id'])).first()
			manager_user = User.query.filter_by(email=i['reporting_manager_email']).first()
			manager_employee = Employees.query.filter_by(user_id=str(manager_user.id)).first()
			setattr(new_employee, 'reporting_manager_id', manager_employee.id)
			db.session.commit()
			db.session.flush()
			db.session.refresh(new_employee)
>>>>>>> 1ae9c7da1f5229400bfc96bd59bc83a4a65f63fd

	except:
		logging.exception('error')



<<<<<<< HEAD

@app.route('/bulk_upload_balance_sheet', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_balance_sheet():
	try:
		if request.method == 'GET':
			return render_template("bulk_upload.html")

		if request.method == 'POST':
			if 'file' not in request.files:
				flash('No file part')
				return redirect(request.url)
			file = request.files['file']

			if file and allowed_file(file.filename)==False:
				print('file')
				flash('No file part')
				return redirect(request.url)

			link_of_file = upload_file(request.files['file'])
			print('main',link_of_file)
			list_of_elemet = read_csv(link_of_file)


			for i in list_of_elemet:
				employee_user = User.query.filter_by(email=i['email']).first()
				employee_employee = Employees.query.filter_by(user_id=str(employee_user.id)).first()		
				i['emp_id'] =  employee_employee.id
				new_balance_sheet = Balance_sheet() 
				for item in i.keys():
					setattr(new_balance_sheet, item, i[item])
				db.session.add(new_balance_sheet)
				db.session.commit()
=======
@app.route('/bulk_upload_balance_sheet', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_balance_sheet():
	try:
		with open('app/controllers/balance_sheet.csv') as csvfile:
		    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		    list_of_elemet = []
		    for index, row in enumerate(reader):
		        if index == 0:
		            keys = row
		        else:
		            list_of_elemet.append(dict(zip(keys[0].split(','), row[0].split(','))))


		for i in list_of_elemet:
			employee_user = User.query.filter_by(email=i['email']).first()
			employee_employee = Employees.query.filter_by(user_id=str(employee_user.id)).first()		
			i['emp_id'] =  employee_employee.id
			new_balance_sheet = Balance_sheet() 
			for item in i.keys():
				setattr(new_balance_sheet, item, i[item])
			db.session.add(new_balance_sheet)
			db.session.commit()
>>>>>>> 1ae9c7da1f5229400bfc96bd59bc83a4a65f63fd

	except:
		logging.exception('error')