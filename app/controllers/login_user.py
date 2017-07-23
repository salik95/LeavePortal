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

@app.route('/')
#@login_required
def index():
    return render_template('index.html')


@app.context_processor
def inject_user():
  # @todo join current user and employee
  employee = Employees.query.get(1)
  return {'user': employee}

@app.context_processor
def inject_date():
  print(datetime.datetime.utcnow())
  return {'now': datetime.datetime.utcnow()}