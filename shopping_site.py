import os

from flask import Flask, render_template, session, request, redirect, url_for, flash  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore 
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

from product_selection.map_user_to_product import *
from product_selection.select_product import Product

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.secret_key = 'hello'

# Rendering Landing Page
@app.route('/', methods=['GET', 'POST'])
def landing_page():
    if request.method == 'POST':
        # Get raw 'who' and 'what' input
        user_details = request.form.get('user_details')
        product_preferences = request.form.get('product_preferences')

        # Store user_details and product_preferences
        session['user_details'] = user_details
        session['product_preferences'] = product_preferences
        
        # Redirecting to index
        return redirect(url_for('index'))
    
    # Rendering landing page
    return render_template('landing_page.html')

# Rending Products Page
@app.route('/index', methods=['GET', 'POST'])
def index():
    # Get who and what from landing page
    user_details = session.get('user_details')
    product_preferences = session.get('product_preferences')

    if request.method == 'POST':
        # Get updated 'what' input and re-render page
        updated_preferences = request.form.get('updated_preferences')
        session['product_preferences'] = updated_preferences

        return redirect(url_for('index'))

    # Call Python function to map inputs to products
    products_list: list[Product] = map_inputs(user_details, product_preferences)

    return render_template('index.html', products_list=products_list)

if __name__ == '__main__':
    app.run(debug=True)