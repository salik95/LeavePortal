from app.models import *
from app import db , app
from flask import request, jsonify
from app.controllers.utilfunc import *
import datetime
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

	settings = Settings.query.filter_by(key='fiscal_year_starting').first()
	fiscal_year =  datetime.datetime.strptime(settings.value , '%B %d')
	employees = Employees.query.all()

	today_date = datetime.date.today()

	##-----------------This will run every day and update the probation value ---------------##

	for i in employees:
		if i.probation == 1:
			days = (today_date- i.date_of_joining).days
			if days >= 90:
				if i != 0:
					setattr(i , 'probation' , 0)
					db.session.commit()
					db.session.flush()
					db.session.refresh(i)

	##-----------------This will run every month and update the genral leaves by 2---------------##
	if today_date.day == 1:
		for i in employees:
			if i.probation == 0:
				if today_date.month == fiscal_year.month -1:
					setattr(i , 'general_leaves_remaining' , i.general_leaves_remaining + 3	)
				else:
					setattr(i , 'general_leaves_remaining' , i.general_leaves_remaining + 2)
				db.session.commit()
				db.session.flush()
				db.session.refresh(i)


	##-----------------This will run every year and update the genral leaves to be max of 25 ---------------##


	if today_date.month == fiscal_year.month  and  today_date.day == fiscal_year.day:
		for i in employees:
			if i.probation == 0:
				if i.general_leaves_remaining > 25:
					setattr(i , 'general_leaves_remaining' , 25)
					db.session.commit()
					db.session.flush()
					db.session.refresh(i)

		
	return jsonify(employee_sqlalchemy_to_list(Employees.query.all()))
