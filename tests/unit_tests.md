# Unit Testing Checklist for Personalized Shopping Site

This checklist outlines all the features and units that need to be tested. Each section corresponds to a specific component or functionality of the application.

## 1. User Inputs
[] Who are you - landing_who()
[] What you want - landing_what()
[] Convert user input to JSON object - input_to_json(self, type) 


## 2. Product Page
[x] Display products - index()
[] Product recommendations - basic_map()
    [x] test function with valid user data and product list
    [] test function with no user preferences
    [] test function an empty product list
    [x] test function edge cases (e.g., user age is 0 or 100)
    [x] test function invalid user data (e.g., missing fields)
[x] Side bar
    [x] test that user details are updated
    [x] test for page refresh with new blog post

## 3. Blogpost
[x] write_blogpost()
    [x] test function for related content
    [x] test function for personalization

## 4. Cookies
[] update_user_details()
[] get_cookie()
[] delete_cookie()

