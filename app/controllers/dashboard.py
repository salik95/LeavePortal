
from app.models import *
from app import db , app
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import login_required , current_user


@app.route('/dashboard/', methods=['GET', 'POST'])

@login_required
def dashboard():

    # user identification checks here i.e. finding out id of user login.
    # user = User.query.get(id)
    # employee = Employee.query.filter(Employee.user_id == user.id)
    
    # template already has user, no need to pass from controller
    employee = Employees.query.get(current_user.get_id())
    history = Balance_sheet.query.filter(Balance_sheet.emp_id == employee.id)
    store = {'history': history}
    return render_template("dashboard/main.html", data = store)
