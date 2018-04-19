from app.models import *
from app import db , app
from flask import request, jsonify, render_template, Response, flash, redirect, url_for
from flask_login import login_required, current_user
from app.controllers.utilfunc import *
from sqlalchemy import asc, and_, or_
from app.resources.notifications import notify
import datetime
import csv


@app.route('/leave_form', methods=['POST'])
@login_required
def leave_form():
	leave_data = request.get_json(force=True)

	if 'from_date' not in leave_data or 'to_date' not in leave_data or 'purpose' not in leave_data or 'leave_type' not in leave_data:
		return error_response_handler("Incomplete Data", 400)
	
	leave_data['emp_id'] = current_user.employee.id

	if current_user.role == "HR Manager":
		leave_data['hr_approval'] = "Approved"

	leave_data['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d")

	if (datetime.datetime.strptime(leave_data['to_date'], "%Y-%m-%d") - datetime.datetime.strptime(leave_data['from_date'], "%Y-%m-%d")).days > current_user.employee.general_leaves_remaining:
		return error_response_handler("Leave request exceeds available leaves request", 400)
	new_leave = Balance_sheet()
	key = list(leave_data.keys())
	for item in key:
		setattr(new_leave, item, leave_data[item])
	try:
		db.session.add(new_leave)
		db.session.commit()
	except:
		db.session.rollback()
		flash(u"Something went wrong. Try again", "error")
		return redirect(url_for("dashboard"))
	leave_dict = {}
	for col_name in Balance_sheet.__mapper__.columns.keys():
		leave_dict[col_name] = getattr(new_leave, col_name)
	
	notify(subject='Leave Request', receiver_id=current_user.employee.manager.user_id)

	return jsonify(leave_dict)


@app.route('/history', methods=['GET'])
@login_required
def leave_all():
	store = {}
	arg_id = request.args.get("id")
	download = request.args.get('download')

	emp_id = None

	if current_user.role == "HR Manager" or current_user.role == "General Manager":

		if arg_id is None:
			emp_id = current_user.employee.id
		elif arg_id != "":
			emp_id = arg_id
			employee = Employees.query.get(emp_id)
			if employee is None:
				return render_template("history.html", data = {'error': "No Such Employee Exist"})
			store.update({'employee' : employee})
		else:
			store.update({'employee' : None})

	else:
		emp_id = current_user.employee.id

	if emp_id:
		history = Balance_sheet.query.filter(Balance_sheet.emp_id == emp_id).order_by(asc(Balance_sheet.from_date)).all()
	else:
		history = None
	store.update({'history' : history})


	if download !=None:

		outfile = open('app/resources/csvfiles/Balance_sheet.csv', 'w')
		outcsv = csv.writer(outfile)
		outcsv.writerow([column.name for column in Balance_sheet.__mapper__.columns])
		[outcsv.writerow([getattr(curr, column.name) for column in Balance_sheet.__mapper__.columns]) for curr in history]
		outfile.close()
		outfile = open('app/resources/csvfiles/Balance_sheet.csv', 'r')
		return Response(
		outfile,
		mimetype="text/csv",
		headers={"Content-disposition":
		         "attachment; filename=Balance_sheet-{} {}.csv".format(employee.first_name , employee.last_name)})


	return render_template("history.html", data = store)



@app.route('/requests', methods=['GET'])
@login_required
def request_all():
	key = Balance_sheet.__mapper__.columns.keys()
	
	if current_user.role == "HR Manager":
		pending = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(or_(and_(Balance_sheet.hr_approval == None, Balance_sheet.manager_approval == 'Approved'), and_(Employees.reporting_manager_id == current_user.employee.id, Balance_sheet.manager_approval == None))).order_by(asc(Balance_sheet.from_date)).all()
		responded = db.session.query(Employees, Balance_sheet).join(Balance_sheet).filter(and_(Balance_sheet.hr_approval != None, Balance_sheet.emp_id != current_user.employee.id)).order_by(asc(Balance_sheet.from_date)).all()

	else:
		pending = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(and_(Employees.reporting_manager_id == current_user.employee.id, Balance_sheet.manager_approval == None)).order_by(asc(Balance_sheet.from_date)).all()
		responded = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
			.filter(and_(Employees.reporting_manager_id == current_user.employee.id, Balance_sheet.manager_approval != None)).order_by(asc(Balance_sheet.from_date)).all()

	requests = {'pending' : pending, 'responded' : responded}

	return render_template("requests.html", data = {'requests': requests})

@app.route('/respond_request', methods=['PUT'])
@login_required
def respond_request():
	response = request.get_json(force=True)
	if 'id' not in response or 'remark' not in response or 'approval' not in response:
		return error_response_handler("Incomplete Data", 400)
	
	leave = Balance_sheet.query.get(response['id'])
	if leave is None:
		return error_response_handler("Not found")
	employee = Employees.query.get(leave.emp_id)
	if employee is None:
		return error_response_handler("Employee for the leave not found")

	if current_user.role == "HR Manager":
		response['hr_remark'] = response['remark']
		response['hr_approval'] = response['approval']

		if response['approval'] == "Approved":
			notify(subject='Leave Approved', receiver_id=employee.user_id)
		elif response['approval'] == "Unapproved":
			notify(subject='Leave Unapproved' , receiver_id=employee.user_id)

		if employee.reporting_manager_id == current_user.employee.id:
			response['manager_remark'] = response['hr_remark']
			response['manager_approval'] = response['hr_approval']
	else:
		if current_user.employee.id != employee.reporting_manager_id:
			return error_response_handler("Unauthorized request", 401)
		response['manager_remark'] = response['remark']
		response['manager_approval'] = response['approval']
		if response['approval'] == "Approved":
			notify(subject='Leave Request', send_hr=True)
		elif response['approval'] == "Unapproved":
			notify(subject='Leave Unapproved' , receiver_id=employee.user_id)

	key = list(response.keys())
	for item in key:
		setattr(leave, item, response[item])
	if leave.manager_approval == "Approved" and leave.hr_approval == "Approved":
		update_employee_leaves_after_approval((leave.to_date - leave.from_date).days, leave.emp_id, leave.leave_type)
	del response['id']
	try:
		db.session.commit()
	except:
		db.session.rollback()
		flash(u"Something went wrong, please try again.", "error")
		return redirect(url_for("dashboard"))
	return jsonify(response)

def update_employee_leaves_after_approval(days, emp_id, leave_type):
	employee = Employees.query.get(emp_id)
	if leave_type == "Medical":
		employee.medical_leaves_availed = employee.medical_leaves_availed+days
		employee.medical_leaves_remaining = employee.medical_leaves_remaining-days
	else:
		employee.general_leaves_availed = employee.general_leaves_availed+days
		employee.general_leaves_remaining = employee.general_leaves_remaining-days

def get_dict_of_sqlalchemy_object(alchemy_object, key, value=None):
	alchemy_list = []
	if alchemy_object is not None:
		for leave_item in alchemy_object:
			temp_dict = {}
			for item in key:
				if value!=None:
					temp_dict[item] = getattr(getattr(leave_item, value), item)
				else:
					temp_dict[item] = getattr(leave_item, item)
			alchemy_list.append(temp_dict)
	return alchemy_list