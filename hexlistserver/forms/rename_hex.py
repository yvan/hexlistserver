from flask.ext.wtf import Form
from wtforms.fields import StringField
from wtforms.validators import DataRequired

class RenameHex(Form):
    hexname = StringField('hexname')

'''
author @yvan
'''