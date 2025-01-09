# Unit Testing Checklist for Personalized Shopping Site

This checklist outlines all the features and units that need to be tested. Each section corresponds to a specific component or functionality of the application.

## 1. User Inputs
[] Who are you - landing_who()
[] What you want - landing_what()
[] Convert user input to JSON object - input_to_json(self, type) 


## 2. Product Page
[] Display products - index()
[] Product recommendations - basic_map()
    [] test function with valid user data and product list
    [] test function with no user preferences
    [] test function an empty product list
    [] test function edge cases (e.g., user age is 0 or 100)
    [] test function invalid user data (e.g., missing fields)

## 3. Blogpost
[] write_blogpost()

## 4. Cookies
[] update_user_details()
[] get_cookie()
[] delete_cookie()

