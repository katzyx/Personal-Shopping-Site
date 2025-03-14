import sys
import json
import time

from product_selection.select_product import Product, BasicSelection
from product_selection.user_input import UserInput
from shopping_site import API_key

# For internal testing
# from select_product import Product, BasicSelection
# from user_input import UserInput
# from key import API_key

def basic_map(user_who, user_what): 
    from shopping_site import product_selector
    
    # Wait for database to be ready if still parsing
    while product_selector is None:
        time.sleep(0.1)
    
    # Extract user info and use keyword lookup
    product_selector.parse_user_jsons(user_who, user_what)
    products_selected = product_selector.keyword_lookup()
    
    return products_selected
    
def map_inputs(retrieved_who, retrieved_what):
    # Get retrieved user inputs and put them into json strings (accessed with user_input.input_who and user_input.input_what)
    user_input = UserInput(API_key, retrieved_who, retrieved_what)
    user_input.parse_user_inputs()
    
    return basic_map(user_input.input_who, user_input.input_what)


# Use for Testing
# if __name__ == "__main__": 
#     user_input = UserInput(API_key, "I am a 21 year old Asian woman with light oily skin", "I am looking for foundation and skincare products under 40$")
#     user_input.parse_user_inputs()
    
#     basic_map(user_input.input_who, user_input.input_what)



