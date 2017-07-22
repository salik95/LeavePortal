# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
                  
from werkzeug import check_password_hash, generate_password_hash
from app import db , app
from app.forms.forms import LoginForm
from app.models import *
from flask_login import login_required ,login_user
from app import login_manager
import datetime

@login_manager.user_loader
def user_loader(email):
    return User.query.filter_by(email = email).first()



@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    # If sign in form is submitted
    form = LoginForm(request.form)
    # Verify the sign in form
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Welcome %s' % user.name)
            return redirect(url_for('index'))
        flash('Wrong email or password', 'error-message')
    return render_template("login/signin.html", form=form)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User(name = form.name.data  , email = form.email.data, 
            password= generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        db.session.flush()
        return redirect(url_for('signin'))
    return render_template("login/signin.html", form=form)


# temporary
@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    # user role checks here
    # user identification checks here i.e. finding out id of user login.
    # user = User.query.get(id)
    # employee = Employee.query.filter(Employee.user_id == user.id)
    employee = Employees.query.get(1)
    history = Balance_sheet.query.filter(Balance_sheet.emp_id == employee.id)
    current_date = datetime.datetime.now()

    dict_dashboard = []

    dict_dashboard.append({'Day' : current_date.strftime("%A"), 'Date' : current_date.strftime("%d"),
        'Month' : current_date.strftime("%B"), 'remaining_leaves' : employee.leaves_remaining,
        'availed_leaves' : employee.leaves_availed})
    for item in history:
        dict_dashboard.append({'id' : item.id, 'from_date' : item.from_date.strftime("%d"),
            'from_month' : item.from_date.strftime("%b"), 'to_date' : item.to_date.strftime("%d"),
            'to_month' : item.to_date.strftime("%b"), 'leave_type' : item.leave_type, 'purpose' : item.purpose,
            'pay' : item.pay, 'hr_remark' : item.hr_remark, 'manager_remark' : item.manager_remark,
            'hr_approval' : item.hr_approval, 'manager_approval' : item.manager_approval})

    return render_template("manager/dashboard.html", dict_dashboard = dict_dashboard)

@app.route('/')
#@login_required
def index():
    return render_template('index.html')


