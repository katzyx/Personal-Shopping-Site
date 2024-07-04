# Imports
import pandas as pd
import numpy as np
import json
import shade_match

PRODUCT_CATEGORIES = {
    'SKINCARE' : ['Cleanser','Exfoliator', 'Makeup Remover', 'Toner', 'Moisturizer', 'Serum', 'Mask', 'Eye Cream'],
    'FACE' : ['Face Primer', 'Foundation', 'Tinted Moisturizer', 'Concealer', 'Blush', 'Bronzer', 'Contour', 'Highlighter', 'Setting Powder', 'Setting Spray'],
    'EYE' : ['Mascara', 'Eyeliner', 'Eyebrow', 'Eyeshadow', 'Eye Primer'],
    'LIP' : ['Lip Gloss', 'Lipstick', 'Lip Oil', 'Lip Plumper', 'Lip Balm', 'Lip Liner']}

USER_WHAT_PROMPTS = ['Products', 'Brand', 'Price', 'Formula']

# Class Definitions
class Product:
    def __init__(self, name, type, brand, color, price, size, formula, ingredients, about, url):
        self.name: str = name # Product name
        self.type: str = type # Product type
        self.brand: str = brand # Product brand
        self.color: list[str] = color# List of all product colors (all shades)
        self.price: float = price # Price of product in CAD
        self.size: str = size# Product size in metric given
        self.formula: str = formula # Product formula
        self.ingredients: list[str] = ingredients# List of ingredients of product
        self.about: str = about # Description of product
        self.url: str = url # URL to product purchasing site


    def get_attribute(self, entry):
        if entry == 'Products': return self.type
        if entry == 'Brand': return self.brand
        if entry == 'Price': return self.price
        if entry == 'Formula': return self.formula


class BasicSelection:
    def __init__(self, csv_file):
        self.csv_file: str = csv_file # Link to csv file
        self.product_database: list[Product] = [] # list of products
        self.user_info: dict = {} # Provided user information

    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)

        for r in range(0, df.shape[0]):            
            # split string from dataset into list
            color = df.iloc[r, 2]
            color_list = color.split(',')

            ingr = df.iloc[r, 7]
            ingr_list = ingr.split(',')

            # Create product object to append to product database
            temp_product = Product(name = df.iloc[r, 0],
                                   type = df.iloc[r, 1],
                                   brand = df.iloc[r, 2],
                                   color = color_list,
                                   price = df.iloc[r, 4],
                                   size = str(df.iloc[r, 5]),
                                   formula = df.iloc[r, 6],
                                   ingredients = ingr_list,
                                   about = df.iloc[r, 8],
                                   url = df.iloc[r, 9]) 
            
            self.product_database.append(temp_product)
    
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

            if user_price_string == '' or 'Not specified' in user_price_string:
                price = [-999,999999]
            elif 'to' in user_price_string:
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
    
    def keyword_lookup(self):
        product_match: dict = {}

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

