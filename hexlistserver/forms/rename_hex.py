from flask.ext.wtf import Form
from wtforms.fields import StringField

class RenameHex(Form):
    hexname = StringField('hexname')

'''
author @yvan
'''