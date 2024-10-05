import os
import time
import sys

from flask import Flask, render_template, make_response, session, request, redirect, url_for, flash  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore 
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

from product_selection.blogpost import Blogpost
from product_selection.map_user_to_product import *
from product_selection.select_product import Product

from product_selection.key import API_key

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.secret_key = 'hello'

def get_cookie_value(cookie_name):
    return request.cookies.get(cookie_name)

# Rendering Landing Page
@app.route('/', methods=['GET', 'POST'])

def landing_who():
    if get_cookie_value('user_details') != "":
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get raw 'who' input
        user_details = request.form.get('user_details')

        # Store user_details 
        session['user_details'] = user_details
        
        # Redirecting to landing_what
        return redirect(url_for('landing_what'))
    
    # Rendering landing whos page
    return render_template('landing_who.html')

@app.route('/landing_what', methods=['GET', 'POST'])
def landing_what():
    if request.method == 'POST':
        # Get raw 'what' input
        product_preferences = request.form.get('product_preferences')

        # Store product_preferences
        session['product_preferences'] = product_preferences
        
        # Redirecting to index
        resp = make_response(redirect(url_for('index')))  # Create a response and redirect
        resp.set_cookie('userdetails', user_details)  # Set the cookie
        return resp
    
    # Rendering landing what page
    return render_template('landing_what.html')

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

    start_time = time.time()
    # Call Python function to map inputs to products
    products_list: list[Product] = map_inputs(user_details, product_preferences)

    # Call Python function to write custom blog post
    blog = Blogpost(API_key, user_details, product_preferences)
    written_blog = blog.write_blogpost()
    
    time_elapsed = "{:.3f}".format(time.time() - start_time)

    return render_template('index.html', products_list=products_list, blog=written_blog, time=time_elapsed, user_details=user_details)

@app.route('/update_user_details', methods=['POST'])
def update_user_details():
    user_details = request.form.get('user_details')  # Get the user details from the form
    session['user_details'] = user_details  # Update the session variable
    resp = make_response(redirect(url_for('index')))  # Create a response and redirect
    resp.set_cookie('userdetails', user_details)  # Set the cookie
    return resp
    
@app.route('/get_cookie')  # Route to retrieve the cookie
def get_cookie():
    username = get_cookie_value('userdetails')  # Use the utility function to get the cookie
    if username:
        return f'Your profile: {username}!'  # Return a message with the username
    else:
        return 'No cookie found!'  # Message if no cookie is set
    
@app.route('/delete_cookie')  # Route to delete the cookie
def delete_cookie():
    resp = make_response("Cookie Deleted")
    resp.set_cookie('userdetails', '', expires=0)  # Delete the cookie by setting its expiration to 0
    return resp

if __name__ == '__main__':
    app.run(debug=True)