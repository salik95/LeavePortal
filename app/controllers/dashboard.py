from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, asc
from app.bin.leaves_update import update_general_leaves
from app.controllers.settings import settings_to_dict
from datetime import datetime
from app.controllers.utilfunc import *

@app.route('/dashboard/', methods=['GET'])
@login_required
def dashboard():
	if request.method == 'GET':

		store = {}
		employee = current_user.employee

		if current_user.role == "HR Manager":
			requests = {}

			pending = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(or_(and_(Balance_sheet.hr_approval == None, Balance_sheet.manager_approval != None), and_(Employees.reporting_manager_id == employee.id, Balance_sheet.manager_approval == None))).order_by(asc(Balance_sheet.from_date)).all()
			requests['pending'] = pending
			requests['responded'] = []
			if len(pending) < 5:
				responded = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(and_(Balance_sheet.hr_approval != None, Balance_sheet.emp_id != employee.id)).order_by(asc(Balance_sheet.from_date)).limit(5-len(pending)).all()
				requests['responded'] = responded

			store.update({'requests' : requests})

		else:
			all_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(Employees.reporting_manager_id == employee.id)
			if all_requests is None:
				manager = False
			else:
				requests = {}
				manager = True
				pending = all_requests.filter(Balance_sheet.manager_approval == None).all()
				requests['pending'] = pending
				requests['responded'] = []
				if len(pending) < 5:
					responded = all_requests.filter(Balance_sheet.manager_approval != None).limit(5-len(pending)).all()
					requests['responded'] = responded

				store.update({'requests' : requests})	
			store.update({'manager' : manager})




		leaves_remaining = update_general_leaves(
			date_of_joining = employee.date_of_joining, 
			last_updated = employee.last_updated,
			leaves_remaining = int(employee.general_leaves_remaining),
			leaves_in_probation = int(settings_to_dict()['probation_leaves_limit']) ,
			first_year = employee.first_year, 
			fiscal_year = settings_to_dict()['fiscal_year_starting']  ,
			probation_period = int(settings_to_dict()['probation_period']),
			leaves_limit = int(settings_to_dict()['general_leaves_limit']),
			leaves_availed = int(employee.general_leaves_availed),
			probation_leaves_limit = int(settings_to_dict()['probation_leaves_limit'])
		)


		leaves_details = {'general_leaves_availed' : employee.general_leaves_availed, 
		'general_leaves_remaining' : leaves_remaining,
		'medical_leaves_availed' : employee.medical_leaves_availed, 
		'medical_leaves_remaining' : employee.medical_leaves_remaining}
		
		employee.general_leaves_remaining = leaves_remaining
		employee.last_updated = datetime.now().date()
		db.session.commit()
		db.session.flush()
		store.update({'history' : employee.balance_sheet, 'user' : employee, 'leaves_details' : leaves_details, 'role':current_user.role})

		return render_template("dashboard.html", data = store)