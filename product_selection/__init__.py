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
    size: str # Product size in metric given
    formula: str # Product formula
    ingredients: list[str] # List of ingredients of product
    about: str # Description of product
    url: str # URL to product purchasing site

class BasicSelection(BaseModel):
    csv_file: str # Link to csv file
    product_database: list[Product] = [] # list of products

    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)
        print("rows: ", df.shape[0])
        print("columns: ", df.shape[1])

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
        
        # print("dataframe: ", df)
        return self.product_database

            
            
