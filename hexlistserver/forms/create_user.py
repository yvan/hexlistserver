from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class CreateUser(Form):
    username = StringField('name', validators=[DataRequired()], render_kw={"placeholder": "Put the name you want here..."})
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "Put the password you want here..."})
    password_two= PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "Put the password you want here, again..."})
'''
author @yvan
'''