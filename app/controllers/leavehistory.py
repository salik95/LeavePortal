from flask import render_template,request
from app import app


@app.route('/mytemp', methods=['GET'])
def mytemp():
	if request.method == 'GET':
		return render_template("dashboard/leavehistory.html")