from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class CreateUser(Form):
    username = StringField('name', validators=[DataRequired()], render_kw={"placeholder": "the name you want"})
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    password_two= PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "password again"})
'''
author @yvan
'''