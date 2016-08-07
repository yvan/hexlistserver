from flask.ext.wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired

class RecoverPassword(Form):
    email = StringField('email', validators=[DataRequired()], render_kw={"placeholder": "your email"})

'''
author @yvan
'''