'''
Description: Defines product class and helper functions to parse and sort product objects
Authors: Floria Fang Zhang, Hope Hadfield, Katherine Zhang, Maisey Perelonia
'''

# Imports
import pandas as pd
import numpy as np
from pydantic import BaseModel
import json
import csv
import math
import user_shaderequest

product_shades = {}
PRODUCT_CATEGORIES = {
    'SKINCARE' : ['Cleanser','Exfoliator', 'Makeup Remover', 'Toner', 'Moisturizer', 'Serum', 'Mask', 'Eye Cream'],
    'FACE' : ['Face Primer', 'Foundation', 'Tinted Moisturizer', 'Concealer', 'Blush', 'Bronzer', 'Contour', 'Highlighter', 'Setting Powder', 'Setting Spray'],
    'EYE' : ['Mascara', 'Eyeliner', 'Eyebrow', 'Eyeshadow', 'Eye Primer'],
    'LIP' : ['Lip Gloss', 'Lipstick', 'Lip Oil', 'Lip Plumper', 'Lip Balm', 'Lip Liner']}

USER_WHAT_PROMPTS = ['Products', 'Brand', 'Price', 'Formula', 'Color']

# Class Definitions
class Product(BaseModel):
    name: str # Product name
    type: str # Product type
    brand: str # Product brand
    color: str # List of all product colors (all shades)
    price: float # Price of product in CAD
    size: str # Product size in metric given
    formula: str # Product formula
    rgb_values: list[int]
    # ingredients: list[str] # List of ingredients of product
    # about: str # Description of product
    # url: str # URL to product purchasing site

    def get_attribute(self, entry):
        if entry == 'Products': return self.type
        if entry == 'Brand': return self.brand
        if entry == 'Price': return self.price
        if entry == 'Formula': return self.formula
        if entry == 'Color': return self.rgb_values
        # if entry == 'RGB': return self.rgb_values


class BasicSelection(BaseModel):
    csv_file: str # Link to csv file
    product_database: list[Product] = [] # list of products
    user_info: dict = {} # Provided user information
    def categorize_products(self):
        with open(self.csv_file, "r", newline="") as csvf:
            reader = csv.DictReader(csvf)
            for row in reader:
                temp_product = Product(name = row["Product Name"],
                    type = row["Type"],
                    brand = row["Brand"],
                    color = row["Shade Name"],
                    price = row["Price (CAD)"],
                    size = row["Size"],
                    formula = row["Formula"],
                    rgb_values = (int(row["R"]), int(row["G"]), int(row["B"])))

                self.product_database.append(temp_product)
                # if prod_shade in product_shades:
                #     product_shades[prod_shade].append((rgb_values, product_name, prod_shade_name))
                # else:
                #     product_shades[prod_shade] = [(rgb_values, product_name, prod_shade_name)]
    
    def parse_user_jsons(self, user_who, user_what):
        # Extract from JSON to dictionary
        self.user_info['who'] = json.loads(user_who)
        self.user_info['what'] = json.loads(user_what)

        # Specify products
        if 'Products' in self.user_info['what']:
            product_list = []
            
            # Parse through list of all products user wants
            for entry in self.user_info['what']['Products'].split(','):
                entry_is_individual_product = True
                
                # If they specified an entire category, add all cateogory products to products list
                for product_cat, cat_list in PRODUCT_CATEGORIES.items():
                    if entry.replace(' ', '').upper().replace('PRODUCTS', '').replace('PRODUCT', '') == product_cat:
                        entry_is_individual_product = False
                        product_list.extend(cat_list)
                
                # Otherwise, if product is individual product, just append to list
                if entry_is_individual_product:
                    product_list.append(entry.strip())

            self.user_info['what']['Products'] = product_list
        
        # Specify price range
        if 'Price' in self.user_info['what']:
            price = []
            user_price_string = self.user_info['what']['Price'].replace('$', '').lower()

            if 'to' in user_price_string:
                price = user_price_string.replace(' ', '').split('to')
                price = [float(i) for i in price]
                price.sort()
            elif 'under' in user_price_string or 'less than' in user_price_string:
                price = [0, float(user_price_string.replace('under', '').replace('less than', ''))]
            elif 'above' in user_price_string or 'more than' in user_price_string:
                price = [float(user_price_string.replace('above', '').replace('more than', '')), 999999]
            elif 'around' in user_price_string:
                price = [float(user_price_string.replace('around', '')) - 5, float(user_price_string.replace('around', '')) + 5]
            else:
                price = [float(user_price_string), float(user_price_string)]
            
            self.user_info['what']['Price'] = price
    # csv_path = "ShadeData.csv"
    # categorize_products(csv_path, product_shades)
    
    def shade_finder(self, user_shade, p):

        val = math.sqrt((user_shade[0] - p[0])**2 + (user_shade[1] - p[1])**2 + (user_shade[2] - p[2])**2)
        return val

    def keyword_lookup(self):
        product_match: dict = {}
        rgb_shade_match = user_shaderequest.chatgpt(self.user_info['what']['Color'])
        x = rgb_shade_match.split(",")
        y = (int(x[0]), int(x[1]), int(x[2]))
  
        # Parse through all products
        for product in self.product_database:
            matches = 0

            # If product is specified and does not match, skip product (put in matchces = 0)
            if 'Products' in self.user_info['what']:
                if product.get_attribute('Products') not in self.user_info['what']['Products']:
                    if matches in product_match:
                        product_match[matches].append(product)
                    else:
                        product_match[matches] = [product]
                    continue
            
            # Otherwise, look at other prompts
            for prompt in USER_WHAT_PROMPTS:
                if prompt in self.user_info['what']:
                    if prompt == 'Price':
                        if product.get_attribute(prompt) in range(int(self.user_info['what'][prompt][0]), int(self.user_info['what'][prompt][1])):
                            matches += 1
                    elif prompt == 'Color':
                        #print(product.get_attribute(prompt))
                        if self.shade_finder(y, product.get_attribute(prompt)) < 100:
                            matches += 1
                    elif product.get_attribute(prompt) in self.user_info['what'][prompt]:
                        matches += 1
            
            if matches in product_match:
                product_match[matches].append(product)
            else:
                product_match[matches] = [product]
        
        top_products: list[Product] = []
        for num_matches in reversed(list(product_match.keys())):
            if len(top_products) >= 2:
                break
            for product in product_match[num_matches]:
                top_products.append(product)
        
        return top_products

            
            
