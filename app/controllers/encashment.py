from app.models import *
from app import db , app
from flask import request, jsonify, render_template, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from flask_weasyprint import HTML, render_pdf
import datetime
from sqlalchemy import asc, and_, or_
from app.resources.notifications import notify
from flask import Flask, render_template, redirect, url_for
import os
import json

def create_pdf(pdf_data):
	resultFile = open('hello.pdf', "w+b")
	pisa.CreatePDF(pdf_data, dest=resultFile)
	resultFile.close()  


@app.route('/encashment', methods = ['GET', 'POST', 'DELETE', 'PUT'])
@login_required
def encashment():
	
	leaves_remaining = current_user.employee.general_leaves_remaining
	salary = current_user.employee.salary

	if request.method == 'GET':

		store = {}
		requests_history = Encashment.query.filter(Encashment.emp_id == current_user.employee.id).order_by(asc(Encashment.time_stamp)).all()
		leaves_onhold = 0

		for item in requests_history:
			if item.hr_approval != item.gm_approval != item.manager_approval != "":
				leaves_onhold += item.leaves_utilized

		store.update({'history' : requests_history, 'leaves_available' : leaves_remaining - leaves_onhold, 'salary' : salary})

		return render_template('encashment.html', data=store)

	if request.method == 'POST':
		encashment_data = request.form.copy()

		if 'amount' not in encashment_data:
			flash(u'Please enter the amount to be encashed', 'error')
			return redirect(url_for('encashment'))
		
		encashment_data['emp_id'] = current_user.employee.id
		encashment_data['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d")
		encashment_data['leaves_utilized'] = float(encashment_data['amount']) / salary

		if current_user.role == 'HR Manager':
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['manager_approval'] = 'Approved'
			notify(subject='new_encashment_request', send_gm=True)

		elif current_user.role == "General Manager":
			encashment_data['gm_approval'] = 'Approved'
			notify(subject='new_encashment_request', send_director=True)
		else:
			if current_user.employee.reporting_manager_id == User.query.filter_by(role='General Manager').first().employee.id:
				encashment_data['manager_approval'] = 'Approved'
			notify(subject='new_encashment_request', receiver_id=current_user.employee.manager.id)

		encashment_request = Encashment()
		for item in list(encashment_data.keys()):
			setattr(encashment_request, item, encashment_data[item])
		try:
			db.session.add(encashment_request)
			db.session.commit()
		except:
			db.session.rollback()
			flash(u'Some internal error occured, please refresh the page.', 'error')
			return redirect(url_for('encashment'))

		flash(u'Your encashment request is sent successfully.', 'success')
		return redirect(url_for('encashment'))

#===========================================================
#Refactor This
	if request.method == 'DELETE':
		arg_id = request.args.get("id")
		if arg_id is None or arg_id == "":
			return error_response_handler("Bad request", 400)
		encashment_request = Encashment.query.get(arg_id)
		if encashment_request is None:
			return error_response_handler("Request ID not found", 404)
		try:
			db.session.delete(encashment_request)
			db.session.commit()
		except:
			db.session.rollback()
			return redirect(url_for('encashment'))
		return jsonify(arg_id)

#==========================================================
#This is not tested
	if request.method == 'PUT':
		encashment_data = request.get_json(force = True)
		if 'id' not in encashment_data or 'amount' not in encashment_data:
			return error_response_handler("Incomplete Data", 400)
		encashment_request = Encashment.query.get(encashment_data['id'])
		if encashment_request is None:
			return error_response_handler("Encashment request not found", 404)
		setattr(encashment_request, 'amount', encashment_data['amount'])
		setattr(encashment_request, 'hr_approval', None)
		setattr(encashment_request, 'manager_approval', None)
		setattr(encashment_request, 'gm_approval', None)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			return redirect(url_for('encashment'))
		return jsonify(encashment_data['amount'])


@app.route('/encashment/requests', methods = ['GET', 'PUT'])
@login_required
def encashment_request():
	if request.method == 'GET':

		requests = {}

		if current_user.role == "HR Manager":
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.hr_approval == None, Encashment.manager_approval == "Approved", Encashment.gm_approval == "Approved", Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.hr_approval != None, Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()

		elif current_user.role == "General Manager":
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.gm_approval == None, Encashment.manager_approval == "Approved", Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.gm_approval != None, Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
		else:
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.manager_approval == None, Employees.reporting_manager_id == current_user.employee.id, Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.manager_approval != None, Employees.reporting_manager_id == current_user.employee.id, Encashment.emp_id != current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
		requests.update({'pending' : pending, 'responded' : responded})

		return render_template('encashment-requests.html', data={'requests': requests})

	if request.method == 'PUT':
		encashment_data = request.get_json(force = True)

		if 'id' not in encashment_data and 'approval' not in encashment_data:
			return error_response_handler("Incomplete Data", 400)

		encashment_request = Encashment.query.get(encashment_data['id'])
		employee = Employees.query.get(encashment_request.emp_id)
		if encashment_request is None:
			return error_response_handler("Encashment request not found", 404)

		if current_user.role == 'HR Manager':
			setattr(encashment_request, 'hr_approval', encashment_data['approval'])
			if encashment_data['approval'] == 'Approved':
				#flash("Encashment form sent")
				notify(subject='Encashment Approved', receiver_id=employee.id)
				notify(subject='Encashment Form', send_hr=True)
			if encashment_data['approval'] == 'Unapproved':
				notify(subject='Encashment Unapproved', receiver_id=employee.id)

		elif current_user.role == 'General Manager':
			setattr(encashment_request, 'gm_approval', encashment_data['approval'])
			if encashment_data['approval'] == 'Approved':
				notify(subject='new_encashment_request', send_hr=True)
			elif encashment_data['approval'] == 'Unapproved':
				notify(subject='encashment_unapproved', receiver_id=employee.id)

		else:
			if employee.reporting_manager_id != current_user.employee.id:
				return error_response_handler("Unauthorized request", 401)
			setattr(encashment_request, 'manager_approval', encashment_data['approval'])
			if encashment_data['approval'] == 'Approved':
				notify(subject='new_encashment_request', send_gm=True)
			elif encashment_data['approval'] == 'Unapproved':
				notify(subject='encashment_unapproved', receiver_id=employee.id)

		if encashment_request.hr_approval == 'Approved' and encashment_request.gm_approval == 'Approved' and encashment_request.manager_approval == 'Approved':
			encashment_user = User.query.get(employee.user_id)

			store = {}
			store.update({'name': employee.first_name + " " + employee.last_name, 'designation' : employee.designation, 'email' : encashment_user.email, 'available_leave_balance' : employee.general_leaves_remaining, 'leaves_encashed' : encashment_request.leaves_utilized, 'amount_encashable' : employee.general_leaves_remaining * employee.salary, 'amount_encashed' : encashment_request.leaves_utilized * employee.salary})

			employee.general_leaves_remaining = employee.general_leaves_remaining - encashment_request.leaves_utilized
			employee.general_leaves_availed = employee.general_leaves_availed + encashment_request.leaves_utilized

			line_manager = Employees.query.get(employee.reporting_manager_id)
			general_manager = Employees.query.filter_by(user_id=((User.query.filter_by(role='General Manager')).first()).id).first()
			hr_manager = Employees.query.filter_by(user_id=((User.query.filter_by(role='HR Manager')).first()).id).first()

			if line_manager.last_name is not None:
				line_manager_name = line_manager.first_name + " " + line_manager.last_name
			else:
				line_manager_name = line_manager.first_name

			db.session.commit()
			

		dirname = os.path.join(app.config['PDF_URL'], 'mypdf.txt')
		store_object = json.dumps(store)
		f = open(dirname,"w")
		f.write(store_object)
		f.close()


		del encashment_data['id']
		encashment_data['redirect_url'] = url_for('encashment_pdf' , _external=True)
		print('******************' , encashment_data['redirect_url'])
		return jsonify(encashment_data)