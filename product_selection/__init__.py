'''
Description:
Authors: Floria Fang Zhang, Hope Hadfield, Katherine Zhang, Maisey Perelonia
'''

# Imports
import pandas as pd
import numpy as np
from pydantic import BaseModel

# Class Definitions
class Product(BaseModel):
    name: str # Product name
    type: str # Product type
    brand: str # Product brand
    color: list[str] # List of all product colors (all shades)
    price: float # Price of product in CAD
    size: dict = dict.fromkeys(['oz', 'g', 'mL'], None) # Product size in ounces, grams, mililleters
    formula: str # Product formula
    ingredients: list[str] # List of ingredients of product
    about: str # Description of product
    url: str # URL to product purchasing site

class BasicSelection(BaseModel):
    csv_file: str # Link to csv file
    # product_databse: list[Product] # list of products
    
    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)
        print("data set: ", self.csv_file)
        print("rows: ", df.shape[0])
        print("columns: ", df.shape[1])

        for r in range(1, df.shape[0]):
            # Create product object to append to product database
            temp_product = Product(name = df.iloc[r, 0],
                                   type = df.iloc[r, 1],
                                   brand = df.iloc[r, 2],
                                   color = df.iloc[r, 3],
                                   price = df.iloc[r, 4],
                                   size = df.iloc[r, 5],
                                   formula = df.iloc[r, 6],
                                   ingredients = df.iloc[r, 7],
                                   about = df.iloc[r, 8],
                                   url = df.iloc[r, 9]) 
            
            # Extract size of product
            # size = df.entry['Size']
            # size = size.split('/')
            # for measure in size:
            #     measure = measure.replace(' ', '')
            #     for key in list(temp_product.size.keys()):
            #         if measure.endswith(key):
            #             temp_product.size[key] = int(measure.split(key)[0])
            
            # self.product_database.append(temp_product)