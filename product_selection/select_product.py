# Imports
import time
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Set
import threading

PRODUCT_CATEGORIES = {
    'SKINCARE' : ['Cleanser','Exfoliator', 'Makeup Remover', 'Toner', 'Moisturizer', 'Serum', 'Mask', 'Eye Cream'],
    'FACE' : ['Face Primer', 'Foundation', 'Tinted Moisturizer', 'Concealer', 'Blush', 'Bronzer', 'Contour', 'Highlighter', 'Setting Powder', 'Setting Spray'],
    'EYE' : ['Mascara', 'Eyeliner', 'Eyebrow', 'Eyeshadow', 'Eye Primer'],
    'LIP' : ['Lip Gloss', 'Lipstick', 'Lip Oil', 'Lip Plumper', 'Lip Balm', 'Lip Liner']}

USER_WHAT_PROMPTS = ['Products', 'Brand', 'Price', 'Formula', 'Colour']

NUMBER_PRODUCTS_RETURNED = 11

# Class Definitions
class Product:
    def __init__(self, name, type, brand, color, price, size, formula, ingredients, about, url, redirect_url):
        self.name: str = name # Product name
        self.type: list[str] = type # Product categories
        self.brand: str = brand # Product brand
        self.color: list[str] = color# List of all product colors (all shades)
        self.price: float = price # Price of product in CAD
        self.size: str = size# Product size in metric given
        self.formula: str = formula # Product formula
        self.ingredients: list[str] = ingredients# List of ingredients of product
        self.about: str = about # Description of product
        self.url: str = url # URL to product image
        self.redirect_url: str = redirect_url # URL to purchasing site


    def get_attribute(self, entry):
        if entry == 'Products': return self.type
        if entry == 'Brand': return self.brand
        if entry == 'Price': return self.price
        if entry == 'Formula': return self.formula
        if entry == 'Colour': return self.color


class BasicSelection:
    def __init__(self, csv_file):
        self.csv_file: str = csv_file # Link to csv file
        self.product_database: list[Product] = [] # list of products
        self.user_info: dict = {} # Provided user information

    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)

        for r in range(0, df.shape[0]):            
            # Convert categories string to list
            categories = df.iloc[r, 3].split(',') if isinstance(df.iloc[r, 3], str) else []
            categories = [cat.strip() for cat in categories]
            
            # Convert shades string to list
            shades = df.iloc[r, 4].split(',') if isinstance(df.iloc[r, 4], str) else []
            shades = [shade.strip() for shade in shades]
            
            # Convert ingredients string to list
            ingr = df.iloc[r, 8] if isinstance(df.iloc[r, 8], str) else ''
            ingr_list = [i.strip() for i in ingr.split(',') if i.strip()]

            # Create product object to append to product database
            temp_product = Product(
                name=df.iloc[r, 1],      # name
                type=categories,          # categories as type
                brand=df.iloc[r, 2],      # brand
                color=shades,            # shades as color
                price=df.iloc[r, 5],      # price
                size=str(df.iloc[r, 6]),  # size
                formula='',              # empty formula
                ingredients=ingr_list,    # ingredients list
                about=df.iloc[r, 7],      # about
                url=df.iloc[r, 10],        # image_url
                redirect_url=df.iloc[r, 11]
            )
            
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
            price_list = [i for i in price[1:-1].split(",") if i.strip()]

            # Handle empty or invalid price input
            if len(price_list) < 2:
                self.user_info['what']['Price'] = [0, 99999999]

            # convert price list to floats
            else:
                for count, element in enumerate(price_list):
                    price_list[count] = float(re.sub(r"[^\d\.]", "", element))           
                self.user_info['what']['Price'] = price_list
        else:
            self.user_info['what']['Price'] = [0,99999999]
    
    def process_product_chunk(self, products: List[Product], user_info: Dict, start_idx: int, end_idx: int) -> Dict[int, List[Product]]:
        product_match: Dict[int, List[Product]] = {}
        
        for product in products[start_idx:end_idx]:
            matches = 0
            
            # Quick check for product type match first
            if 'Products' in user_info['what']:
                product_matches = False
                requested_products = set(user_info['what']['Products'])  # Convert to set for O(1) lookup
                if any(prod in requested_products for prod in product.type) or any(prod in product.name for prod in requested_products):
                    product_matches = True
                    matches += 1
                else:
                    if matches in product_match:
                        product_match[matches].append(product)
                    else:
                        product_match[matches] = [product]
                    continue
            
            # Check other criteria
            if 'Price' in user_info['what']:
                price_range = user_info['what']['Price']
                if price_range[0] <= product.price <= price_range[1]:
                    matches += 1
            
            if 'Brand' in user_info['what']:
                if user_info['what']['Brand'].lower() == product.brand.lower():
                    matches += 1
            
            if 'Colour' in user_info['what']:
                requested_color = user_info['what']['Colour'].lower()
                if any(requested_color in shade.lower() for shade in product.color):
                    matches += 1
            
            if matches in product_match:
                product_match[matches].append(product)
            else:
                product_match[matches] = [product]
            
        return product_match

    def merge_results(self, results: List[Dict[int, List[Product]]]) -> Dict[int, List[Product]]:
        merged: Dict[int, List[Product]] = {}
        for result in results:
            for matches, products in result.items():
                if matches in merged:
                    merged[matches].extend(products)
                else:
                    merged[matches] = products
        return merged

    def keyword_lookup(self):
        print(f"Starting keyword lookup with {os.cpu_count()} threads")
        start_time = time.time()
        
        # Determine optimal chunk size based on CPU count
        chunk_size = max(len(self.product_database) // (os.cpu_count() or 4), 1)
        chunks = [(i, min(i + chunk_size, len(self.product_database))) 
                 for i in range(0, len(self.product_database), chunk_size)]
        
        # Process chunks in parallel
        results = []
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = [
                executor.submit(self.process_product_chunk, 
                              self.product_database, 
                              self.user_info, 
                              start, 
                              end) 
                for start, end in chunks
            ]
            results = [f.result() for f in futures]
        
        # Merge results
        product_match = self.merge_results(results)
        
        # Select top products
        top_products: List[Product] = []
        for matches in sorted(product_match.keys(), reverse=True):
            if matches == 0:
                break
            products = product_match[matches]
            remaining = NUMBER_PRODUCTS_RETURNED - len(top_products)
            if remaining <= 0:
                break
            top_products.extend(products[:remaining])
        
        print(f"Keyword lookup completed in {time.time() - start_time:.2f} seconds")
        return top_products
