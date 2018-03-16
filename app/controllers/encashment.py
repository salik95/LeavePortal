from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
import datetime

@app.route('/encashment_form', methods = ['GET', 'POST'])
def leave_encashment():
	if request.method == 'POST':
		encashment_data = request.get_json(force = True)

		if 'amount' not in encashment_data or 'leaves_utilized' not in encashment_data:
			return error_response_handler("Incomplete Data", 400)
		
		encashment_data['emp_id'] = current_user.employee.id
		encashment_data['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d")

		if current_user.role = 'HR Manager':
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['manager_approval'] = 'Approved'

		if current_user.role = "General Manager":
			encashment_data['hr_approval'] = 'Approved'
			encashment_data['gm_approval'] = 'Approved'

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

	if request.method = 'GET':
		return jsonify({'leaves_available' : current_user.employee.general_leaves_remaining, 'salary' : current_user.employee.salary})