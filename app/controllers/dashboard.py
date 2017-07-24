from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required , current_user
from sqlalchemy import and_

@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
  employee = Employees.query.get(current_user.get_id())
  history = Balance_sheet.query.filter(Balance_sheet.emp_id == employee.id)
  pending_requests = db.session.query(Employees, Balance_sheet).join(Balance_sheet)\
    .filter(and_(Employees.reporting_manager == employee.id, Balance_sheet.manager_approval == None))

  store = {'history' : history, 'pending_requests' : pending_requests}
  return render_template("dashboard/main.html", data = store)