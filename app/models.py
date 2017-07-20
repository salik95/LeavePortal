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
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __init__(self, email, password):
        self.email = email
        self.password = password  

class Employees(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    first_name = db.Column(db.String(45), nullable = False)
    last_name = db.Column(db.String(45), nullable = True)
    reporting_manager = db.Column(db.Integer, nullable = True)
    designation = db.Column(db.String(45), nullable = False)
    department = db.Column(db.String(45), nullable = False)
    total_leaves_allowed = db.Column(db.Integer, nullable = False)
    leaves_availed = db.Column(db.Integer, nullable = False)
    leaves_remaining = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, first_name, last_name, reporting_manager, designation, department,
        total_leaves_allowed, leaves_availed, leaves_remaining):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.reporting_manager = reporting_manager
        self.designation = designation
        self.department = department
        self.total_leaves_allowed = total_leaves_allowed
        self.leaves_availed = leaves_availed
        self.leaves_remaining = leaves_remaining

class Balance_sheet(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable = False)
    from_date = db.Column(db.DateTime(), nullable = False)
    to_date = db.Column(db.DateTime(), nullable = False)
    leave_type = db.Column(db.Enum('General','Medical'), nullable = False)
    purpose = db.Column(db.String(200), nullable = False)
    pay = db.Column(db.Enum('Payed','Unpayed'), nullable = False)
    hr_remark = db.Column(db.String(128), nullable = True)
    manager_remark = db.Column(db.String(128), nullable = True)
    hr_approval = db.Column(db.Integer, nullable = False)
    manager_approval = db.Column(db.Integer, nullable = False)

    def __init__(self, emp_id, from_date, to_date, leave_type, purpose, pay, hr_remark, manager_remark,
        hr_approval, manager_approval):
        self.emp_id = emp_id
        self.from_date
        self.to_date
        self.leave_type
        self.purpose
        self.pay
        self.hr_remark
        self.manager_remark
        self.hr_approval
        self.manager_approval