from app.models import *
from app import db , app
from flask import jsonify, request, make_response
from flask_login import login_required, current_user
from app.controllers.utilfunc import *

@app.route('/settings', methods=['GET','PUT'])
@login_required
def settings():
	if request.method == 'GET':
		return jsonify(settings_to_dict())

	#Creating a seperate route to update settings through getting id in the URL, displays the id in URL that can be
	#exploited. So, excepting the changes through PUT verb with the same URL. One drawback is that all the rows in the
	#table would have to be fetched.

	if request.method == 'PUT':
		update = request.get_json(force=True)
		#As getting all the rows can be an overhead, but there won't be a lot of settings, so it is negligible.
		data = Settings.query.all()
		if data is None:
			return error_response_handler("No Settings Found")
		for item in data:
			if item.key == update['key']:
				item.value = update['value']
		db.session.commit()
		return jsonify(update)


def settings_to_dict():
		setting = Settings.query.all()
		data_setting = {}
		for item in setting:
			data_setting[item.key] = item.value
		return data_setting