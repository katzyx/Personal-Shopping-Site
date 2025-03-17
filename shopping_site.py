import os
import time
import sys
from threading import Thread

from flask import Flask, render_template, make_response, session, request, redirect, url_for, flash, jsonify  # type: ignore
from flask_bootstrap import Bootstrap # type: ignore 
from flask_moment import Moment # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, SubmitField, validators # type: ignore

from product_selection.blogpost import Blogpost
from product_selection.map_user_to_product import *
from product_selection.select_product import Product

# from product_selection.key import API_key
from product_selection.user_input import UserInput

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.secret_key = 'hello'
results_storage = {}

API_key = os.environ.get("OPENAI_API_KEY")

def initialize_database():
    print("Begin parsing dataset")
    csv_path = "./product_selection/products.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()
    print("Done parsing dataset")
    return select

# Global variable to store the BasicSelection instance
product_selector = None

# Start database parsing in background thread when app starts
def start_background_parsing():
    global product_selector
    product_selector = initialize_database()

background_thread = Thread(target=start_background_parsing)
background_thread.daemon = True
background_thread.start()

def get_cookie_value(cookie_name):
    return request.cookies.get(cookie_name)

# Rendering Landing Page
@app.route('/', methods=['GET', 'POST'])

def landing_who():
    
    #session.permanent = False

    if 'userdetails' in request.cookies:
        return redirect(url_for('landing_what'))
    
    if request.method == 'POST':
        # Get raw 'who' input
        user_details = request.form.get('user_details')

        # Store user_details 
        session['user_details'] = user_details

        if user_details is None:
            print("ERROR: USER DETAILS IS NULL")
            user_details = ""  # Default to an empty string or a fallback value
        
        resp = make_response(redirect(url_for('landing_what')))  # Create a response and redirect
        resp.set_cookie('userdetails', user_details)  # Set the cookie
        # Redirecting to landing_what
        return resp
    
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
        return redirect(url_for('index'))
    
    # Rendering landing what page
    return render_template('landing_what.html')

@app.route('/check_status', methods=['GET'])
def check_status():
    # Check if the background task is complete by checking session data
    if 'products_list' in results_storage:
        # If results are ready, send back 'done' and show the results
        return jsonify({"status": "done"})
    else:
        # Otherwise, just say "still processing"
        return jsonify({"status": "processing"})

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
    
    thread = Thread(target=getting_products, args=(user_details, product_preferences))
    thread.start()

    # Render loading page until computation is done
    return render_template('loading.html')

def getting_products(user_details, product_preferences):
    start_time = time.time()
    results_storage.pop('products_list', None)
    # Call Python function to map inputs to products
    products_list: list[Product] = map_inputs(user_details, product_preferences)
    print("Products returned")
    # Call Python function to write custom blog post
    blog = Blogpost(API_key, user_details, product_preferences)
    written_blog = blog.write_blogpost()
    print("Blog written")
    
    time_elapsed = "{:.3f}".format(time.time() - start_time)
    print(products_list)
    if len(products_list) == 0:
        print("empty")
        products_list = []
    
    results_storage['products_list'] = products_list
    results_storage['blog'] = written_blog
    results_storage['time_elapsed'] = time_elapsed
    results_storage['user_details'] = user_details
    results_storage['product_preferences'] = product_preferences

@app.route('/display_results', methods=['GET', 'POST'])
def display_results():
    # Retrieve the results from session
    print("Trying to display results")
    products_list = results_storage.get('products_list', [])
    blog = results_storage.get('blog', '')
    time_elapsed = results_storage.get('time_elapsed', '')
    user_details = results_storage.get('user_details', '')
    product_preferences = results_storage.get('product_preferences', '')

    # Render the results page with the computed data
    return render_template('index.html', products_list=products_list, blog=blog, time=time_elapsed, user_details=user_details, product_preferences=product_preferences)

@app.route('/update_user_details', methods=['POST'])
def update_user_details():
    data = request.get_json()
    current_details = data.get('current_details', '')
    new_details = data.get('new_details', '')

    # Create UserInput instance
    user_input = UserInput(API_key, current_details, new_details)

    # Merge descriptions
    merged_description = user_input.merge_descriptions(current_details, new_details)
    
    # Update user_details in session
    session['user_details'] = merged_description
    
    # Preserve the existing product_preferences instead of clearing them
    product_preferences = session.get('product_preferences', '')

    # Create a new UserInput instance with the merged description and preserved preferences
    user_input = UserInput(API_key, merged_description, product_preferences)
    
    return jsonify({'merged_description': merged_description})

    
@app.route('/get_cookie')  # Route to retrieve the cookie
def get_cookie():
    username = get_cookie_value('userdetails')  # Use the utility function to get the cookie
    if username:
        return f'Your profile: {username}!'  # Return a message with the username
    else:
        return 'No cookie found!'  # Message if no cookie is set

@app.route('/delete_cookie')
def delete_cookie():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('userdetails')  # Remove the 'username' cookie
    return resp

@app.route('/merge_preview', methods=['POST'])
def merge_preview():
    data = request.get_json()
    current_details = data.get('current_details', '')
    new_details = data.get('new_details', '')

    # Create UserInput instance
    user_input = UserInput(API_key, current_details, new_details)

    # Merge descriptions
    merged_description = user_input.merge_descriptions(current_details, new_details)

    return jsonify({'merged_description': merged_description})

if __name__ == '__main__':
    app.run(debug=True)