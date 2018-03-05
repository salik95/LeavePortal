from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required, current_user

@app.route('/employee', methods=['GET', 'POST'])
def employee():
	if request.method == 'GET':
		return "in progress"

	if request.method == 'POST':
		data_employee = request.get_json(force=True)

		new_employee = Employees()

		key = list(data_employee.keys())
		for item in key:
			setattr(new_employee, item, data_employee[item])
			
		db.session.add(new_employee)
		db.session.commit()
		db.session.flush()
		return "success"