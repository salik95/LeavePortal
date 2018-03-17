import csv
from app.models import *
from app import db , app
from flask import request, jsonify
from flask_login import login_required, current_user
from app.controllers.settings import settings_to_dict
from sqlalchemy import and_, or_
from app.controllers.utilfunc import *
import logging 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/bulk_upload_user', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template("bulk_upload.html")



#@app.route('/bulk_upload_user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_user():

	try:
		if request.method == 'GET':
			return render_template("bulk_upload.html")


		with open('app/controllers/temp.csv') as csvfile:
		    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		    #csv_keys = reader[0] 
		    list_of_elemet = []
		    for index, row in enumerate(reader):
		        if index == 0:
		            keys = row
		        else:
		            list_of_elemet.append(dict(zip(keys[0].split(','), row[0].split(','))))
			
		list_of_employee_object = []
		list_of_user_object = []

		for i in list_of_elemet:
			one_user = User(i['email'], "hoh123", i['role'])
			db.session.add(one_user)
			db.session.commit()
			del i['email'] 
			del i['role']
			i['user_id'] = one_user.id
			new_employee = Employees() 
			for item in i.keys():
				if item != 'reporting_manager_email':
					setattr(new_employee, item, i[item])
			list_of_employee_object.append(new_employee)

		db.session.add_all(list_of_employee_object)
		db.session.commit()

		list_of_employee_object = []



		for i in list_of_elemet:
			new_employee = Employees.query.filter_by(user_id=str(i['user_id'])).first()
			manager_user = User.query.filter_by(email=i['reporting_manager_email']).first()
			manager_employee = Employees.query.filter_by(user_id=str(manager_user.id)).first()
			setattr(new_employee, 'reporting_manager_id', manager_employee.id)
			db.session.commit()
			db.session.flush()
			db.session.refresh(new_employee)

	except:
		logging.exception('error')



@app.route('/bulk_upload_balance_sheet', methods=['GET', 'POST', 'PUT', 'DELETE'])
def bulk_upload_balance_sheet():
	try:
		with open('app/controllers/balance_sheet.csv') as csvfile:
		    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		    list_of_elemet = []
		    for index, row in enumerate(reader):
		        if index == 0:
		            keys = row
		        else:
		            list_of_elemet.append(dict(zip(keys[0].split(','), row[0].split(','))))


		for i in list_of_elemet:
			employee_user = User.query.filter_by(email=i['email']).first()
			employee_employee = Employees.query.filter_by(user_id=str(employee_user.id)).first()		
			i['emp_id'] =  employee_employee.id
			new_balance_sheet = Balance_sheet() 
			for item in i.keys():
				setattr(new_balance_sheet, item, i[item])
			db.session.add(new_balance_sheet)
			db.session.commit()

	except:
		logging.exception('error')