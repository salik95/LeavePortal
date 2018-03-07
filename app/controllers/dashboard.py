from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_
from app.controllers.settings import settings_to_dict

@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
	if request.method == 'GET':
		employee = current_user.employee
		pending_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(and_(Employees.reporting_manager_id == employee.id, Balance_sheet.manager_approval == None))

		leaves_details = {'general_leaves_availed' : employee.general_leaves_availed, 
		'general_leaves_remaining' : int(settings_to_dict()['general_leaves_limit']) - employee.general_leaves_availed,
		'medical_leaves_availed' : employee.medical_leaves_availed, 
		'medical_leaves_remaining' : int(settings_to_dict()['medical_leaves_limit']) - employee.medical_leaves_availed}
		
		store = {'history' : employee.balance_sheet, 'pending_requests' : pending_requests, 'user' : employee,
			'leaves_details' : leaves_details}
		return render_template("dashboard/main.html", data = store)