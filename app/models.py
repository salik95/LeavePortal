from app import db


class User(db.Model):

	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(128), nullable = False, unique = True)
	password = db.Column(db.String(128), nullable = False)

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

	def __init__(self, email, password):
		self.email = email
		self.password = password

	def __repr__(self):
		return '%d' % (self.id)

class Employees(db.Model):


	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	first_name = db.Column(db.String(45), nullable = False)
	last_name = db.Column(db.String(45), nullable = True)
	reporting_manager_name = db.Column(db.String(128), nullable = True)
	reporting_manager_email = db.Column(db.String(128), nullable = True)
	designation = db.Column(db.String(45), nullable = False)
	department = db.Column(db.String(45), nullable = False)
	general_leaves_remaining = db.Column(db.Integer, nullable = False)
	medical_leaves_remaining = db.Column(db.Integer, nullable = False)
	general_leaves_availed = db.Column(db.Integer, nullable = False)
	medical_leaves_availed = db.Column(db.Integer, nullable = False)
	date_of_joining = db.Column(db.Date(), nullable = False)

	def __init__(self, user_id, first_name, last_name, reporting_manager_name, reporting_manager_email, 
		designation, department, general_leaves_remaining, medical_leaves_remaining, general_leaves_availed, 
		medical_leaves_availed, date_of_joining):
		self.user_id = user_id
		self.first_name = first_name
		self.last_name = last_name
		self.reporting_manager_name = reporting_manager_name
		self.reporting_manager_email = reporting_manager_email
		self.designation = designation
		self.department = department
		self.general_leaves_remaining = general_leaves_remaining
		self.medical_leaves_remaining = medical_leaves_remaining
		self.general_leaves_availed = general_leaves_availed
		self.medical_leaves_availed = medical_leaves_availed
		self.date_of_joining = date_of_joining

class Balance_sheet(db.Model):

	id = db.Column(db.Integer, primary_key = True)
	emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable = False)
	from_date = db.Column(db.Date(), nullable = False)
	to_date = db.Column(db.Date(), nullable = False)
	leave_type = db.Column(db.Enum('General','Medical'), nullable = False)
	purpose = db.Column(db.String(200), nullable = False)
	pay = db.Column(db.Enum('Payed','Unpayed'), nullable = False)
	hr_remark = db.Column(db.String(128), nullable = True)
	manager_remark = db.Column(db.String(128), nullable = True)
	manager_approval = db.Column(db.Enum('Approved','Unapproved'), nullable = True)

	def __init__(self, emp_id, from_date, to_date, leave_type, purpose, pay, hr_remark, manager_remark,
		manager_approval):
		self.emp_id = emp_id
		self.from_date = from_date
		self.to_date = to_date
		self.leave_type = leave_type
		self.purpose = purpose
		self.pay = pay
		self.hr_remark = hr_remark
		self.manager_remark = manager_remark
		self.manager_approval = manager_approval

class Settings(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	key = db.Column(db.String(45), nullable = False)
	value = db.Column(db.String(45), nullable = False)

	def __init__(self, key, value):
		self.key = key
		self.value = value