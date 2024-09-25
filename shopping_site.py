import os
from flask import Flask, render_template, session, request, redirect, url_for, flash  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_details = request.form.get('user_details')
        product_preferences = request.form.get('product_preferences')
        # Process the form data here (e.g., log, store in DB, etc.)
        return render_template('index.html', user_details=user_details, product_preferences=product_preferences)
    return render_template('landing_page.html')


@app.route('/', methods=['GET', 'POST'])
def landing_page():
    return render_template('landing_page.html')

