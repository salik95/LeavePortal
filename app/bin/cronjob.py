import datetime
from app.resources.notifications  import notify

from sqlalchemy import text

from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *


@app.route('/scheduling')


def scheduling():
	sql = text('select name from penguins')
	result = db.engine.execute("SELECT * FROM balance_sheet WHERE  manager_approval IS NULL \
	OR  `hr_approval` IS NULL ")
	names = []
	for row in result:
	    names.append(row[0])


	# Use all the SQL you like



	cur = db.engine.execute("SELECT * FROM balance_sheet WHERE  manager_approval IS NULL \
	OR  `hr_approval` IS NULL ")
	# print all the first cell of all the rows
	dict_of_employees = {}
	send_email_to_HR_manager = False
	for row in cur:
		today = datetime.datetime.now().date()
		diffrence  = (today - row[-1]).days
		if diffrence >= 2:
			if row[-2] == None: 	send_email_to_HR_manager = True

			if int(row[1]) in list(dict_of_employees.keys()):
				if row[-2] == None:
					dict_of_employees[int(row[1])]['hr_approval'] = row[-2] 
				elif row[-3] == None:
					dict_of_employees[int(row[1])]['manager_approval'] = row[-3] 
			else:
				dict_of_employees[int(row[1])]  = {'hr_approval':row[-2] , 'manager_approval':row[-3] }





	sending_email_and_password = {}
	cur = db.engine.execute('SELECT * FROM  configuration')
	for row in cur:
		sending_email_and_password[row[1]] = row[2]




			

	if send_email_to_HR_manager == True:
		cur = db.engine.execute('SELECT email FROM  user WHERE role = "HR Manager"')
		for row in cur:
			print('hr' , row[0])
			full_dict = {'senders_email':sending_email_and_password['email_address'] ,\
						'password':sending_email_and_password['password'],\
						'recievers_email':row[0]}
			notify( hr_email = row[0] )
			break

	for i in list_of_employee_id:
		full_dict = {'senders_email':sending_email_and_password['email_address'] ,\
						'password':sending_email_and_password['password'],\
						'recievers_email':i}
		notify(recievers_id = i)
		break

	return ('', 204)