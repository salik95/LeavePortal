from app import db


class User(db.Model):

    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(128),  nullable=True)
    email    = db.Column(db.String(128),  nullable=False, unique=True)

    password = db.Column(db.String(192),  nullable=False)

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

    def __init__(self, name, email, password):
        self.name     = name
        self.email    = email
        self.password = password
    def __repr__(self):
        return '<User %r>' % (self.name)  



        