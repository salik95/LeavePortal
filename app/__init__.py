# Import flask and template operators
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

#from app.mod_auth.models import User

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

'''@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)
'''
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from app.controllers.login_user import * 

