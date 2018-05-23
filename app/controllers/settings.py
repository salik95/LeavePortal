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
		if 'gazetted_holidays' in update:
			for holiday in update['gazetted_holidays']:
		setattr(User.query.filter_by(role='Director').first(), 'email', update['director_email'])
		
		#As getting all the rows can be an overhead, but there won't be a lot of settings, so it is negligible.
		data = Settings.query.all()
		if data is None:
			return flash(u'Some internal error occurred, please refresh and try again.', 'error')
		for item in data:
			if item.key in update:
				item.value = update[item.key]
		try:
			db.session.commit()
		except:
			db.session.rollback()
			flash(u'Something went wrong, please try again.', 'error')
			return redirect('/settings')
		flash(u'Application settings updated successfully.', 'success')
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
