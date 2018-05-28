from app.models import *
from app import db , app
from flask import jsonify, request, make_response, render_template, flash, redirect
from flask_login import login_required, current_user
from app.controllers.utilfunc import *
import datetime, dateutil.parser

@app.route('/settings', methods=['GET','POST'])
@login_required
@is_hq_admin
def settings():
	if request.method == 'GET':
		return render_template('settings.html', data=settings_to_dict())

	#Creating a seperate route to update settings through getting id in the URL, displays the id in URL that can be
	#exploited. So, excepting the changes through PUT verb with the same URL. One drawback is that all the rows in the
	#table would have to be fetched.

	if request.method == 'POST':
		update = request.form.copy()
		flash_data = {}
		if 'form-holidays' in update:
			flash_data.update({'for': 'form-holidays'})
			count = len(update.getlist('gazetted_holidays[name]'))
			fields = ['id', 'date', 'month', 'name', 'religion']
			collection = []
			for index in range(count):
				item = {z[0]:update.getlist('gazetted_holidays['+z[0]+']')[index] for z in zip(fields)}
				collection.append(item)
			for holiday in collection:
				if holiday['id'] is not "":
					if holiday['id'].split(';')[0] == 'delete':
						gazetted_holiday = Gazetted_holidays.query.get(holiday['id'].split(';')[1])
						db.session.delete(gazetted_holiday)
					else:
						gazetted_holiday = Gazetted_holidays.query.get(holiday['id'])
						del holiday['id']
						for attr in list(holiday.keys()):
							setattr(gazetted_holiday, attr, holiday[attr])
				else:
					gazetted_holiday = Gazetted_holidays()
					del holiday['id']
					for attr in list(holiday.keys()):
						setattr(gazetted_holiday, attr, holiday[attr])
					db.session.add(gazetted_holiday)
			flash_data.update({'text': 'Gazetted Holidays updated successfully.'})

		else:
			flash_data.update({'for': 'form-settings'})
			setattr(User.query.filter_by(role='Director').first(), 'email', update['director_email'])
			
			#As getting all the rows can be an overhead, but there won't be a lot of settings, so it is negligible.
			data = Settings.query.all()
			if data is None:
				return flash(u'Some internal error occurred, please refresh and try again.', 'error')
			for item in data:
				if item.key in update:
					item.value = update[item.key]
			flash_data.update({'text': 'Application settings updated successfully.'})

		try:
			db.session.commit()
		except:
			db.session.rollback()
			flash_data.update({'text': 'Something went wrong, please try again.'})		
			flash(flash_data, 'error')
			return redirect('/settings')
		flash(flash_data, 'success')
		return redirect('/settings')

def settings_to_dict():
		setting = Settings.query.all()
		data_setting = {}
		for item in setting:
			data_setting[item.key] = item.value
		data_setting['gazetted_holidays'] = all_gazetted_holidays_list()
		return data_setting

def all_gazetted_holidays_list():
	return Gazetted_holidays.query.all()

def gazetted_holidays_list(religion='Other'):
	holiday_string = Gazetted_holidays.query.filter(Gazetted_holidays.religion.in_(('All', religion))).all()
	holidays = []
	for item in holiday_string:
		hs = datetime.datetime.strptime((str(datetime.datetime.now().year) + " " + item.month + " " + item.date), "%Y %B %d")
		holidays.append(hs)
	return holidays

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format) 
