from app import  app
from flask import  render_template, Flask, render_template
from flask_login import login_required
from flask_weasyprint import HTML, render_pdf
import os
import json




@app.route('/encashment_pdf', methods = ['GET'])
@login_required
def encashment_pdf():

	dirname = os.path.join(app.config['PDF_URL'], 'mypdf.txt')
	store = json.load(open(dirname,"r"))
	print(store['line_manager_status'])
	html = render_template('encashment-approval-form.html', **store )

	pdf = HTML(string=html)

	return render_pdf(pdf)