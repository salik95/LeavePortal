from app.models import *
from app import db , app
from flask import request, jsonify
from app.controllers.utilfunc import *
#from app.controllers.employee import employee_sqlalchemy_to_list
from datetime import datetime 

def employee_sqlalchemy_to_list(alchemyObject):
	col_names = Employees.__mapper__.columns.keys()
	employee_all = []
	for value in alchemyObject:
		temp_dict = {}
		for item in col_names:
			temp_dict[item] = getattr(value, item)
		employee_all.append(temp_dict)
	return employee_all 

@app.route('/leaves_update/')


def leaves_update():

	today_date = datetime.now()
	print ('day' , today_date.day , 'month' , today_date.month)
	if today_date.month == 1 and  today_date.day == 1:
		65+5

	if today_date.day == 1:
		55+5
		### chcckimg every day
	

	return jsonify(employee_sqlalchemy_to_list(Employees.query.all()))
	

		