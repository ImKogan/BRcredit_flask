'''
forms.py

forms for admin
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DecimalField
from wtforms.validators import DataRequired

class TermForm(FlaskForm):
    ''' terms form for admin management of loan term types '''
    name = name = StringField('Name')
    installments = IntegerField('Installments', validators=[DataRequired()])
    rate = DecimalField('Rate', validators=[DataRequired()])
    submit = SubmitField('Submit')

