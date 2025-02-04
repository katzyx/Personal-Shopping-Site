# Imports
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import re
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import List, Dict

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
        self.type: list[str] = type # Product categories
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


def parse_product_row(row) -> Product:
    """Helper function to parse a single product row"""
    # Convert categories string to list
    categories = row[3].split(',') if isinstance(row[3], str) else []
    categories = [cat.strip() for cat in categories]
    
    # Convert shades string to list
    shades = row[4].split(',') if isinstance(row[4], str) else []
    shades = [shade.strip() for shade in shades]
    
    # Convert ingredients string to list
    ingr = row[8] if isinstance(row[8], str) else ''
    ingr_list = [i.strip() for i in ingr.split(',') if i.strip()]

    # Create and return product object
    return Product(
        name=row[1],          # name
        type=categories,      # categories as type
        brand=row[2],        # brand
        color=shades,        # shades as color
        price=row[5],        # price
        size=str(row[6]),    # size
        formula='',          # empty formula
        ingredients=ingr_list,# ingredients list
        about=row[7],        # about
        url=row[10]          # image_url
    )

def process_product_chunk(products: List[Product], user_info: Dict, start_idx: int, end_idx: int) -> Dict[int, List[Product]]:
    """Helper function to process a chunk of products for keyword matching"""
    product_match: Dict[int, List[Product]] = {}
    
    for product in products[start_idx:end_idx]:
        matches = 0

        # If products are specified, check if any of the requested products match
        if 'Products' in user_info['what']:
            product_matches = False
            for requested_product in user_info['what']['Products']:
                if requested_product in product.type:
                    product_matches = True
                    break
            
            if not product_matches:
                if matches in product_match:
                    product_match[matches].append(product)
                else:
                    product_match[matches] = [product]
                continue
        
        # Check other prompts
        for prompt in USER_WHAT_PROMPTS:
            if prompt in user_info['what']:
                if prompt == 'Price':
                    if product.get_attribute(prompt) in range(int(user_info['what'][prompt][0]), int(user_info['what'][prompt][1])):
                        matches += 1
                elif prompt == 'Products':
                    matches += 1  # Already handled above
                elif prompt == 'Colour':
                    requested_color = user_info['what'][prompt].lower()
                    for shade in product.color:
                        if requested_color in shade.lower():
                            matches += 1
                            break
                elif product.get_attribute(prompt) in user_info['what'][prompt]:
                    matches += 1
        
        if matches in product_match:
            product_match[matches].append(product)
        else:
            product_match[matches] = [product]
            
    return product_match

class BasicSelection:
    def __init__(self, csv_file):
        self.csv_file: str = csv_file
        self.product_database: list[Product] = []
        self.user_info: dict = {}
        self.lock = threading.Lock()  # Add thread lock for thread safety

    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)
        
        # Create thread pool and process rows in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Map each row to a Product object
            self.product_database = list(executor.map(
                parse_product_row,
                [df.iloc[r] for r in range(df.shape[0])]
            ))

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
    
    def keyword_lookup(self):
        # Determine chunk size for parallel processing
        chunk_size = max(len(self.product_database) // 4, 1)
        chunks = [(i, min(i + chunk_size, len(self.product_database))) 
                 for i in range(0, len(self.product_database), chunk_size)]
        
        # Process chunks in parallel
        product_matches: Dict[int, List[Product]] = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_chunk = {
                executor.submit(
                    process_product_chunk, 
                    self.product_database, 
                    self.user_info, 
                    start, 
                    end
                ): (start, end) for start, end in chunks
            }
            
            # Combine results from all chunks
            for future in future_to_chunk:
                chunk_matches = future.result()
                for matches, products in chunk_matches.items():
                    if matches in product_matches:
                        product_matches[matches].extend(products)
                    else:
                        product_matches[matches] = products

        # Choose top products
        top_products: List[Product] = []
        matches_rev = sorted(product_matches.keys(), reverse=True)
        
        for num_matches in matches_rev:
            if num_matches == 0 or len(top_products) >= NUMBER_PRODUCTS_RETURNED:
                break
            products = product_matches[num_matches]
            top_products.extend(products[:NUMBER_PRODUCTS_RETURNED - len(top_products)])

        return top_products
