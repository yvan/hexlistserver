from flask.ext.wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired

class InputEmail(Form):
    email = StringField('email', validators=[DataRequired()], render_kw={"placeholder": "your email"})
    email_two = StringField('email_two', validators=[DataRequired()], render_kw={"placeholder": "your email again"})

'''
author @yvan
'''