import sys
import json
from select_product import Product, BasicSelection
from user_input import UserInput
from key import API_key

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "ProductDataset.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()

    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    products_selected = select.keyword_lookup()
    
    # Provide top 3 recommended products to user
    for product in products_selected:
        print(product.brand, product.name)
    

# Uses JSON strings from GPT
if __name__ == "__main__": 
    user_input = UserInput(API_key, "I am a 21 year old Asian woman with light oily skin", "I am looking for foundation and skincare products under 40$")
    user_input.parse_user_inputs()
    
    basic_map(user_input.input_who, user_input.input_what)



