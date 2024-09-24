import os
from flask import Flask, render_template, session, redirect, url_for, flash  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

template_dir = os.path.abspath('./prod_website/html')
app = Flask(__name__, template_folder=template_dir)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('landing_page.html')