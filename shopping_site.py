import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators

template_dir = os.path.abspath('./prod_website/html')
app = Flask(__name__, template_folder=template_dir)
bootstrap = Bootstrap(app)
# moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('landing_page.html')