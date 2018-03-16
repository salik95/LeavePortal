from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
import datetime
from sqlalchemy import asc, and_, or_

@app.route('/encashment', methods = ['GET', 'POST', 'DELETE', 'PUT'])
def encashment():
	
	if request.method == 'GET':
		store = {}
		requests_history = Encashment.query.filter(Encashment.emp_id == current_user.employee.id).order_by(asc(Encashment.time_stamp)).all()
		store.update({'history' : requests_history, 'leaves_available' : current_user.employee.general_leaves_remaining, 'salary' : current_user.employee.salary})
		return jsonify(store)

	if request.method == 'POST':
		encashment_data = request.get_json(force = True)

		if 'amount' not in encashment_data or 'leaves_utilized' not in encashment_data:
			return error_response_handler("Incomplete Data", 400)
		
		encashment_data['emp_id'] = current_user.employee.id
		encashment_data['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d")

		if current_user.role == 'HR Manager':
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['manager_approval'] = 'Approved'

		if current_user.role == "General Manager":
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['gm_approval'] = 'Approved'
		if User.query.get(Employees.query.get(current_user.employee.reporting_manager_id).user_id).role == "HR Manager":
			encashment_data['hr_approval'] = 'Approved'

		encashment_request = Encashment()
		for item in list(encashment_data.keys()):
			setattr(encashment_request, item, encashment_data[item])
		db.session.add(encashment_request)
		db.session.commit()
		db.session.flush()

		encashment_dict = {}
		for col_name in Encashment.__mapper__.columns.keys():
			encashment_dict[col_name] = getattr(encashment_request, col_name)

		return jsonify(encashment_dict)

#===========================================================
#Refactor This
	if request.method == 'DELETE':
		arg_id = request.args.get("id")
		if arg_id is None or arg_id == "":
			return error_response_handler("Bad request", 400)
		encashment_request = Encashment.query.get(arg_id)
		if encashment_request is None:
			return error_response_handler("Request ID not found", 404)
		db.delete(encashment_request)
		db.commit()
		db.flush()
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
		db.commit()
		db.flush()
		return jsonify(encashment_data['amount'])


@app.route('/encashment/requests', methods = ['GET', 'PUT'])
def encashment_request():
	if request.method == 'GET':

		requests = {}

		if current_user.role == "HR Manager":
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.hr_approval == None, Encashment.manager_approval != None, Encashment.gm_approval != None)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(Encashment.hr_approval != None).order_by(asc(Encashment.time_stamp)).all()

		elif current_user.role == "General Manager":
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.gm_approval == None, Encashment.manager_approval != None)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(Encashment.gm_approval != None).order_by(asc(Encashment.time_stamp)).all()
		else:
			pending = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.manager_approval == None, Employees.reporting_manager_id == current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
			responded = db.session.query(Employees, Encashment).join(Encashment).filter(and_(Encashment.manager_approval != None, Employees.reporting_manager_id == current_user.employee.id)).order_by(asc(Encashment.time_stamp)).all()
		requests.update({'pending' : pending, 'responded' : responded})

		return jsonify(requests)

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

		elif current_user.role == 'General Manager':
			setattr(encashment_request, 'gm_approval', encashment_data['approval'])
		else:
			if employee.reporting_manager_id != current_user.employee.id:
				return error_response_handler("Unauthorized request", 401)
			setattr(encashment_request, 'manager_approval', encashment_data['approval'])

		if encashment_request.hr_approval == 'Approved' and encashment_request.gm_approval == 'Approved' and encashment_request.manager_approval == 'Approved' :
			employee.general_leaves_remaining = employee.general_leaves_remaining - encashment_request.leaves_utilized
			employee.general_leaves_availed = employee.general_leaves_availed + encashment_request.leaves_utilized
		
		del encashment_data['id']
		
		return jsonify(encashment_data)