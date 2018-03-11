from app.models import *
from app import db , app
from flask import request, jsonify
from app.controllers.utilfunc import *
#from app.controllers.employee import employee_sqlalchemy_to_list
import datetime
#from datetime import datetime 
from app import db , app


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

	settings = Settings.query.filter_by(key='fiscal_year_starting')
	print( settings.fiscal_year_starting)
	employees = Employees.query.all()

	today_date = datetime.date.today()

	print(Employees.query.all()[1].date_of_joining)

	for i in employees:
		if i.probation == 1:
			days = (today_date- i.date_of_joining).days
			if days == 90:
				setattr(i , 'probation' , 0)
				db.session.commit()
				db.session.flush()
				db.session.refresh(i)

	if today_date.day == 11:
		for i in employees:
			if i.probation == 0:
				if today_date.month == 12:
					setattr(i , 'general_leaves_remaining' , i.general_leaves_remaining + 2.0833333333333333	)
				else:
					setattr(i , 'general_leaves_remaining' , i.general_leaves_remaining + 2)
				db.session.commit()
				db.session.flush()
				db.session.refresh(i)



	#if today_date.month == 1 and  today_date.day == 1:

		

		### chcckimg every day
	

	return jsonify(employee_sqlalchemy_to_list(Employees.query.all()))
