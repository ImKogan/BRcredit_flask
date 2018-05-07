from datetime import date, datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    payment = db.Column(db.Numeric())
    principal_pmt = db.Column(db.Numeric())
    interest_pmt = db.Column(db.Numeric())
    penalty = db.Column(db.Integer)
    scheduled_date = db.Column(db.DateTime)
    payment_date = db.Column(db.DateTime)
    paid = db.Column(db.Integer)
    paid_by_guarantor = db.Column(db.Integer)

    loan = db.relationship("Loan",
        foreign_keys=[loan_id],
        backref='payments')

class Loan(db.Model):
    __tablename__ = 'loan'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'))
    status = db.Column(db.String(64), default='good')
    missed_payments = db.Column(db.Integer, default=0)
    principal = db.Column(db.Numeric())
    outstanding = db.Column(db.Numeric())
    terms_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    loan_date = db.Column(db.DateTime())
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    guarantor_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    borrower = db.relationship("User",
        foreign_keys=[borrower_id],
        backref='borrow_loans')

    guarantor = db.relationship("User",
        foreign_keys=[guarantor_id],
        backref='guarantee_loans')

    terms = db.relationship("Terms",
        foreign_keys=[terms_id],
        backref='loans')

    application = db.relationship("Application",
        foreign_keys=[application_id],
        uselist=False,
        backref='loan')

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric())
    status = db.Column(db.Integer, default = 0)
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime())
    decision_at = db.Column(db.DateTime())
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    guarantor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    connection_id = db.Column(db.Integer, db.ForeignKey('connection.id'))
    
    terms_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    message = db.Column(db.String(256))
    borrower_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    guarantor_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    borrower_finances_id = db.Column(db.Integer, db.ForeignKey('finances.id'))
    guarantor_finances_id = db.Column(db.Integer, db.ForeignKey('finances.id'))
  
    # status is (0 by default, 1 when borrower submits application,
    # 2 when submitted by guarantor, 3 when rejected, 4 when approved)

    approved_by = db.relationship("User",
        foreign_keys=[approved_by_id],
        backref='processed_applications')

    processed_by = db.relationship("User",
        foreign_keys=[processed_by_id],
        backref='approved_applications')

    borrower = db.relationship("User",
        foreign_keys=[borrower_id],
        backref='borrow_applications')

    guarantor = db.relationship("User",
        foreign_keys=[guarantor_id],
        backref='guarantee_applications')

    borrower_address = db.relationship("Address",
        foreign_keys=[borrower_address_id],
        backref='borrower_address_applications')

    guarantor_address = db.relationship("Address",
        foreign_keys=[guarantor_address_id],
        backref='guarantor_address_applications')

    borrower_finances= db.relationship("Finances",
        foreign_keys=[borrower_finances_id],
        backref='borrower_finances_applications')

    guarantor_finances = db.relationship("Finances",
        foreign_keys=[guarantor_finances_id],
        backref='guarantor_finances_applications')

    connection = db.relationship("Connect",
        foreign_keys=[connection_id],
        uselist=False,
        backref='application')

    terms = db.relationship("Terms",
        foreign_keys=[terms_id],
        backref='applications')

    def __init__(self, **kwargs):
        super(Application, self).__init__(**kwargs)

class Finances(db.Model):
    __tablename__ = 'finances'
    id = db.Column(db.Integer, primary_key=True)
    salary = db.Column(db.Integer)
    occupation = db.Column(db.String(64))
    employer = db.Column(db.String(64))
    time_employed = db.Column(db.Integer)
    employment_status = db.Column(db.Integer)
    # (employment_status = 0 if unemployed, 1 if employed, 2 if self employed)

    def __init__(self, **kwargs):
        super(Finances, self).__init__(**kwargs)

    def __repr__(self):
        return '<Finances(%r, %r, %r, %r)>' % (
                    self.salary, self.occupation,
                    self.employer, self.time_employed)

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    street = db.Column(db.String(64))
    house = db.Column(db.Integer)
    apartment = db.Column(db.String(16))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    country = db.Column(db.String(64))
    zipcode = db.Column(db.Integer)

    user = db.relationship('User', backref='addresses')

    def __init__(self, **kwargs):
        super(Address, self).__init__(**kwargs)

    def __repr__(self):
        return '<Address(%r, %r, %r, %r, %r, %r, %r)>' % (
                    self.street, self.house, self.apartment,
                    self.city, self.state, self.country, self.zipcode)

class Terms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    installments = db.Column(db.Integer)
    rate = db.Column(db.DECIMAL(precision=2))

    def __repr__(self):
        return '<Terms(%d, %d)>' % (self.installments, self.rate)

class Connect(db.Model):
    __tablename__ = 'connection'
    id = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    guarantor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(64), default='pending')
    amount = db.Column(db.Numeric())
    message = db.Column(db.String(256))
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Connect, self).__init__(**kwargs)

    def __repr__(self):
        return '<Connect (%r)>' % self.amount

    def connect_guarantor(self, email):
        pass

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    cpf = db.Column(db.Integer)
    dob = db.Column(db.Date())

    connection_borrowers = db.relationship(
        'Connect',
        foreign_keys=[Connect.borrower_id],
        backref='borrower',
        lazy='dynamic')
    connection_guarantors = db.relationship(
        'Connect',
        foreign_keys=[Connect.guarantor_id],
        backref='guarantor',
        lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BRCREDIT_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(name='User').first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def is_administrator(self):
        if self.role:
            if self.role.id == 2:
                return True
        else:
            return False

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.email

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name
