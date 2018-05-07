from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

class TermForm(FlaskForm):
    name = name = StringField('Name')
    installments = IntegerField('Installments', validators=[DataRequired()])
    rate = DecimalField('Rate', validators=[DataRequired()])
    submit = SubmitField('Submit')