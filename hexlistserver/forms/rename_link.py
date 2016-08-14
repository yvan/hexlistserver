from flask.ext.wtf import Form
from wtforms.fields import StringField

class RenameLink(Form):
    hexname = StringField('hexname')

'''
author @yvan
'''