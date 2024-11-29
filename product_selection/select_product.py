# Imports
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import re

PRODUCT_CATEGORIES = {
    'SKINCARE' : ['Cleanser','Exfoliator', 'Makeup Remover', 'Toner', 'Moisturizer', 'Serum', 'Mask', 'Eye Cream'],
    'FACE' : ['Face Primer', 'Foundation', 'Tinted Moisturizer', 'Concealer', 'Blush', 'Bronzer', 'Contour', 'Highlighter', 'Setting Powder', 'Setting Spray'],
    'EYE' : ['Mascara', 'Eyeliner', 'Eyebrow', 'Eyeshadow', 'Eye Primer'],
    'LIP' : ['Lip Gloss', 'Lipstick', 'Lip Oil', 'Lip Plumper', 'Lip Balm', 'Lip Liner']}

USER_WHAT_PROMPTS = ['Products', 'Brand', 'Price', 'Formula']

NUMBER_PRODUCTS_RETURNED = 11

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
                    product_list.append(entry.strip().title())

            self.user_info['what']['Products'] = product_list
        
        # Deal with price
        if 'Price' in self.user_info['what']:
            price = self.user_info['what']['Price']
            price = str(price).replace('\'','').replace('\"', '')
            print("price:")
            print(price)
            price_list = [i for i in price[1:-1].split(",") if i.strip()]
            for count, element in enumerate(price_list):
                price_list[count] = float(re.sub("[^\d\.]", "", element))
            self.user_info['what']['Price'] = price_list
        else:
            self.user_info['what']['Price'] = [-np.inf,np.inf]
    
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
            
        # for num_matches, products in product_match.items():
        #     product_list = []
        #     for product in products:
        #         product_list.append(product.name)
        #     print(num_matches, product_list)

        # Choose the top products
        top_products: list[Product] = []

        matches_rev = list(product_match.keys())
        matches_rev.sort(reverse=True)
        for num_matches in matches_rev:
            if num_matches == 0:
                break
            if len(top_products) >= NUMBER_PRODUCTS_RETURNED:
                break
            for product in product_match[num_matches]:
                if len(top_products) >= NUMBER_PRODUCTS_RETURNED:
                    break
                top_products.append(product)
                
        return top_products

