'''
    primary file with app logic
'''

import os

from flask import Flask, render_template

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

@app.route('/')
def hello():
    return 'heyo!'
