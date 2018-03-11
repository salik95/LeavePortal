from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_, or_

@app.route('/dashboard/', methods=['GET'])
def dashboard():
	if request.method == 'GET':
		store = {}
		employee = current_user.employee

		if current_user.role == "HR Manager":

			manager_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(and_(Employees.reporting_manager_id == employee.id, Balance_sheet.manager_approval == None)).all()

			hr_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(Balance_sheet.hr_approval == None).all()

			store.update({'manager_requests' : manager_requests, 'hr_requests' : hr_requests})

		else:
			requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(Employees.reporting_manager_id == employee.id)
			if requests.first() is None:
				manager = False
			else:
				manager = True
				pending_requests = requests.filter(Balance_sheet.manager_approval == None)
				store.update({'pending_requests' : pending_requests})
			store.update({'manager' : manager})

		leaves_details = {'general_leaves_availed' : employee.general_leaves_availed, 
		'general_leaves_remaining' : employee.general_leaves_remaining,
		'medical_leaves_availed' : employee.medical_leaves_availed, 
		'medical_leaves_remaining' : employee.medical_leaves_remaining}
		
		store.update({'history' : employee.balance_sheet, 'user' : employee, 'leaves_details' : leaves_details, 'role':current_user.role})

		return render_template("dashboard/main.html", data = store)