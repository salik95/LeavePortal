from app import db


class User(db.Model):

	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(128), nullable = False, unique = True)
	password = db.Column(db.String(128), nullable = False)
	role = db.Column(db.Enum('Employee','HR Manager', 'General Manager'), nullable = False)

	def is_active(self):
		"""True, as all users are active."""
		return True

	def get_id(self):
		"""Return the email address to satisfy Flask-Login's requirements."""
		return self.id

	def is_authenticated(self):
		"""Return True if the user is authenticated."""
		return self.authenticated

	def is_anonymous(self):
		"""False, as anonymous users aren't supported."""
		return False

	def __init__(self, email, password, role):
		self.email = email
		self.password = password
		self.role = role

	def __repr__(self):
		return '%d' % (self.id)

class Employees(db.Model):

	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	first_name = db.Column(db.String(45), nullable = False)
	last_name = db.Column(db.String(45), nullable = True)
	reporting_manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable = True)
	designation = db.Column(db.String(45), nullable = False)
	department = db.Column(db.String(45), nullable = False)
	general_leaves_availed = db.Column(db.Integer, nullable = False)
	medical_leaves_availed = db.Column(db.Integer, nullable = False)
	date_of_joining = db.Column(db.Date(), nullable = False)

	user = db.relationship('User', uselist=False, backref=db.backref('employee', uselist=False), 
		lazy='joined', foreign_keys=[user_id])
	
	balance_sheet = db.relationship('Balance_sheet', backref='employee', lazy='joined')
	
	manager = db.relationship('Employees', backref=db.backref('subordinates', lazy='dynamic'), 
		remote_side=[id], lazy='joined', foreign_keys=[reporting_manager_id])

class Balance_sheet(db.Model):

	id = db.Column(db.Integer, primary_key = True)
	emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable = False)
	from_date = db.Column(db.Date(), nullable = False)
	to_date = db.Column(db.Date(), nullable = False)
	leave_type = db.Column(db.Enum('General','Medical'), nullable = False)
	purpose = db.Column(db.String(200), nullable = False)
	hr_remark = db.Column(db.String(128), nullable = True)
	hr_approval = db.Column(db.Enum('Approved','Unapproved'), nullable = True)
	manager_remark = db.Column(db.String(128), nullable = True)
	manager_approval = db.Column(db.Enum('Approved','Unapproved'), nullable = True)


class Settings(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	key = db.Column(db.String(45), nullable = False)
	value = db.Column(db.String(45), nullable = False)

	def __init__(self, key, value):
		self.key = key
		self.value = value