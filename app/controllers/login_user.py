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
			if user and user.password == form.password.data:
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)
				return redirect(url_for('dashboard'))
			flash('Wrong email or password', 'error-message')
		return render_template("login.html", form=form)

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


'''@app.route('/signup/', methods=['GET', 'POST'])
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

'''