from flask.ext.wtf import Form
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired

class ResetPassword(Form):
    password = PasswordField('password', validators=[DataRequired()], render_kw={"placeholder": "new password"})
    password_two= PasswordField('password_two', validators=[DataRequired()], render_kw={"placeholder": "new password again"})

'''
author @yvan
'''