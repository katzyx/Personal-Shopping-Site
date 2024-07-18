from __init__ import Product, BasicSelection
import csv
import math

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "ShadeData.csv"
    select = BasicSelection(csv_file=csv_path)
    
    select.categorize_products()
    
    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    products_selected = select.keyword_lookup()
    
    # Provide top 3 recommended products to user
    for product in products_selected:
        print(product.brand, product.name)
    

# Uses JSON strings from GPT
if __name__ == "__main__": 
    input_who = '{"Age":"21","Sex":"Female","Ethnicity":"Asian","Skin Tone":"Light Neutral"}'
    input_what = '{"Products":"Lipstick","Price":"$20 to $60", "Formula":"Cream", "Color": "Red"}'

    basic_map(input_who, input_what)



