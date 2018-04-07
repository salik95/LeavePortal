# Import flask dependencies
from flask import Blueprint, request, render_template, \
				  flash, g, session, redirect, url_for
				  
from werkzeug import check_password_hash, generate_password_hash
from app import db , app
from app.forms.forms import LoginForm
from app.models import *
from flask_login import login_required, login_user, current_user, logout_user
from app import login_manager
import datetime


@login_manager.user_loader
def user_loader(id):
	return User.query.get(id)

@app.route('/', methods=['GET', 'POST'])
def index():
	if  current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	else:
		form = LoginForm(request.form)
		if form.validate_on_submit():
			user = User.query.filter_by(email=form.email.data).first()
			if user and check_password_hash(user.password, form.password.data):
				user.authenticated = True
				try:
					db.session.add(user)
					db.session.commit()
				except:
					db.session.rollback()
					return redirect(url_for('index'))
				login_user(user, remember=True)
				return redirect(url_for('dashboard'))
			flash('Email or password you entered is invalid', 'error')
		return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_callback():
	return redirect(url_for('index'))

@app.context_processor
def inject_user():
	id = current_user.get_id()
	if id is not None:
		employee = Employees.query.get(id)
		return {'user': employee}
	else:
		return {}

@app.context_processor
def inject_date():
	print(datetime.datetime.utcnow())
	return {'now': datetime.datetime.utcnow()}