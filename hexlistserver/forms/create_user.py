from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class CreateUser(Form):
    username = StringField('name', validators=[DataRequired()], render_kw={"placeholder": "your username"})
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    password_two= PasswordField('password_two', validators=[DataRequired()], render_kw={"placeholder": "password again"})
'''
author @yvan
'''