from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class TextareaForm(Form):
    links = TextAreaField('Links', validators=[DataRequired()], render_kw={"placeholder": "Put your links here..."})

'''
author @yvan
'''