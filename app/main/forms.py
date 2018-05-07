from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User, Connect


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ConnectForm(FlaskForm):
    """docstring for ClassName"""
    guarantor_email = StringField('Guarantor Email', 
        validators=[DataRequired(), Length(1, 64), Email()])
    amount = IntegerField('Loan amount requested to guarantee')
    message = TextAreaField('Message to guarantor')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(ConnectForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email address does not have an account.')
        elif field.data == self.user.email:
            raise ValidationError('Can not use self as guarantor')

class PersonalInfoForm(FlaskForm):
    firstname = StringField('First Name:', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    cpf = IntegerField('CPF:')
    dob = DateField('Date of Birth:')
    submit = SubmitField('Next')

class AddressForm(FlaskForm):
    street = StringField('Street:', validators=[DataRequired()])
    house = IntegerField('House:', validators=[DataRequired()])
    apartment = StringField('Apartment:')
    city = StringField('City:', validators=[DataRequired()])
    state = StringField('State:', validators=[DataRequired()])
    country = StringField('Country:', validators=[DataRequired()])
    zipcode = IntegerField('Zipcode:', validators=[DataRequired()])
    submit = SubmitField('Next')

class FinancesForm(FlaskForm):
    salary = IntegerField('Salary:', validators=[DataRequired()])
    occupation = StringField('Occupation:', validators=[DataRequired()])
    employer = StringField('Employer:', validators=[DataRequired()])
    time_employed = IntegerField('Years Employed:', validators=[DataRequired()])
    employment_status = SelectField('Employment Status:',
    choices=[(1, 'Employed'), (0, 'Unemployed'), (2, 'Self Employed')],
        validators=[DataRequired()], coerce=int)
    submit = SubmitField('Next')

class ReviewApplication(FlaskForm):
    amount = IntegerField('Amount:')
    rate = DecimalField('Rate %')
    installments = IntegerField('Installments:')
    payment = DecimalField('Payment:')

