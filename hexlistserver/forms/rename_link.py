from flask.ext.wtf import Form
from wtforms.fields import StringField

class RenameLink(Form):
    linkdescription = StringField('linkdescription')

'''
author @yvan
'''