from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import and_

@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
	if request.method == 'GET':
		employee = current_user.employee
		pending_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(and_(Employees.reporting_manager_id == employee.id, Balance_sheet.manager_approval == None))

		print(employee.first_name)

		store = {'history' : employee.balance_sheet, 'pending_requests' : pending_requests}
		return render_template("dashboard/main.html", data = store)

	if request.method == 'POST':
		print('Data to be recieved')