from app.models import *
from app import db , app
from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_weasyprint import HTML, render_pdf
import datetime
from sqlalchemy import asc, and_, or_
from app.resources.notifications import notify

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
			# @todo render with flash error
			return error_response_handler("Incomplete Data", 400)
		
		encashment_data['emp_id'] = current_user.employee.id
		encashment_data['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d")
		encashment_data['leaves_utilized'] = float(encashment_data['amount']) / salary

		if current_user.role == 'HR Manager':
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['manager_approval'] = 'Approved'
			notify(subject='Encashment request', send_gm=True)

		elif current_user.role == "General Manager":
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['gm_approval'] = 'Approved'
			notify(subject='Encashment request', send_director=True)
		else:
			notify(subject='Encashment request', receiver_id=current_user.employee.manager.id)

		encashment_request = Encashment()
		for item in list(encashment_data.keys()):
			setattr(encashment_request, item, encashment_data[item])
		db.session.add(encashment_request)
		db.session.commit()
		db.session.flush()

		encashment_dict = {}
		for col_name in Encashment.__mapper__.columns.keys():
			encashment_dict[col_name] = getattr(encashment_request, col_name)

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
		db.session.delete(encashment_request)
		db.session.commit()
		db.session.flush()
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
		db.session.commit()
		db.session.flush()
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
				notify(subject='Encashment request', send_hr=True)
			if encashment_data['approval'] == 'Unapproved':
				notify(subject='Encashment Unapproved', receiver_id=employee.id)
		else:
			if employee.reporting_manager_id != current_user.employee.id:
				return error_response_handler("Unauthorized request", 401)
			setattr(encashment_request, 'manager_approval', encashment_data['approval'])
			if encashment_data['approval'] == 'Approved':
				notify(subject='Encashment request', send_gm=True)
			if encashment_data['approval'] == 'Unapproved':
				notify(subject='Encashment Unapproved', receiver_id=employee.id)

		if encashment_request.hr_approval == 'Approved' and encashment_request.gm_approval == 'Approved' and encashment_request.manager_approval == 'Approved':
			encashment_user = User.query.get(employee.user_id)
			
			store = {}
			store.update({'name': employee.first_name + " " + employee.last_name, 'designation' : employee.designation, 'email' : encashment_user.email, 'available_leave_balance' : employee.general_leaves_remaining, 'leaves_encashed' : encashment_request.leaves_utilized, 'amount_encashable' : employee.general_leaves_remaining * employee.salary, 'amount_encashed' : encashment_request.leaves_utilized * employee.salary})

			employee.general_leaves_remaining = employee.general_leaves_remaining - encashment_request.leaves_utilized
			employee.general_leaves_availed = employee.general_leaves_availed + encashment_request.leaves_utilized

			line_manager = Employees.query.get(employee.reporting_manager_id)
			general_manager = Employees.query.filter_by(user_id=((User.query.filter_by(role='General Manager')).first()).id).first()
			hr_manager = Employees.query.filter_by(user_id=((User.query.filter_by(role='HR Manager')).first()).id).first()

			store.update({'remaining_leave_balance': employee.general_leaves_remaining, 'line_manager' : line_manager.first_name + " " + line_manager.last_name, 'line_manager_status' : encashment_request.manager_approval, 'general_manager' : general_manager.first_name + " " + general_manager.last_name, 'general_manager_status' : encashment_request.gm_approval, 'hr_manager' : hr_manager.first_name + " " + hr_manager.last_name, 'hr_manager_status' : encashment_request.hr_approval})
			html = render_template("encashment-approval-form.html", data = store)
			return render_pdf(HTML(string=html))

		
		del encashment_data['id']
		
		db.session.commit()
		db.session.flush()
		
		return jsonify(encashment_data)