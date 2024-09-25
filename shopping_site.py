import os
from flask import Flask, render_template, session, redirect, url_for, flash  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('landing_page.html')