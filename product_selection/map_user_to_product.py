import sys
import json

from product_selection.select_product import Product, BasicSelection
from product_selection.user_input import UserInput
from product_selection.key import API_key

# For internal testing
# from select_product import Product, BasicSelection
# from user_input import UserInput
# from key import API_key

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "./product_selection/ProductDataset.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()

    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    products_selected = select.keyword_lookup()
    
    # Provide top 11 recommended products to user
    # for product in products_selected:
    #     print(product.brand, product.name)
    return products_selected
    
def map_inputs(retrieved_who, retrieved_what):
    # Get retrieved user inputs and put them into json strings (accessed with user_input.input_who and user_input.input_what)
    user_input = UserInput(API_key, retrieved_who, retrieved_what)
    user_input.parse_user_inputs()
    
    basic_map(user_input.input_who, user_input.input_what)


# Use for Testing
# if __name__ == "__main__": 
#     user_input = UserInput(API_key, "I am a 21 year old Asian woman with light oily skin", "I am looking for foundation and skincare products under 40$")
#     user_input.parse_user_inputs()
    
#     basic_map(user_input.input_who, user_input.input_what)



