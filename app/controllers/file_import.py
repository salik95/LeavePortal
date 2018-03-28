import csv
from app.models import *
from app import db , app
from flask import request, jsonify, render_template , redirect
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *
import logging 
import os
from werkzeug.utils import secure_filename
from flask import flash
from app.resources.util_functions import *
from datetime import datetime

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





@app.route('/import', methods=['GET', 'POST'])
def bulk_import():


	if request.method == 'GET':
		return render_template("import.html")

	if request.method == 'POST':
		
		if 'employees' not in request.files and 'balances' not in request.files :
			flash('CSV file is not uploaded')
			return redirect(request.url)


		file = request.files['employees']
		if file and allowed_file(file.filename)==False:
			print('***************')
			file = request.files['balances']
			flash('CSV file is not uploaded')
			return redirect(request.url)
		if request.files['balances'] and allowed_file(request.files['balances'].filename)==False:
			flash('CSV file is not uploaded')
			return redirect(request.url)

		try:

			link_of_file = upload_file(request.files['employees'])
			list_of_elemet = read_csv(link_of_file)
			list_of_employee_object = []
			for i in list_of_elemet:
				one_user = User(i['email'], "hoh123", i['role'])
				db.session.add(one_user)
				db.session.commit()
				del i['email'] 
				del i['role']
				i['user_id'] = one_user.id
				i['first_year'] = True if is_first_year(fiscal_year= settings_to_dict()['fiscal_year_starting'],\
						                  			doj=i['date_of_joining'] ,\
						                   			probation_period=int(settings_to_dict()['probation_period'])) == 1 else False
				i['last_updated'] = datetime.now().date()

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
			flash('User file is successfully uploaded' , 'success')

		except:
			flash('Somethinh is wrong with User file' , 'error')
			db.session.rollback()
			pass

		#*************************************UPload balancesheet************************************
		try:
			link_of_file = upload_file(request.files['balances'])
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
			flash('Balance Sheet file is successfully uploaded' , 'success')
			return redirect(request.url)

		except:
			db.session.rollback()
			flash('Somethinh is wrong with Balance Sheet file ' , 'error')
			return redirect(request.url)



