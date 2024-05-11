'''
Description:
Authors: Floria Fang Zhang, Hope Hadfield, Katherine Zhang, Maisey Perelonia
'''

# Imports
import pandas as pd
from pydantic import BaseModel

# Class Definitions
class Product(BaseModel):
    name: str # Product name
    type: str # Product type
    color: list[str] # List of all product colors (all shades)
    price: float # Price of product in CAD
    size: dict = dict.fromkeys(['oz', 'g', 'mL'], None) # Product size in ounces, grams, mililleters
    formula: str # Product formula
    ingredients: list[str] # List of ingredients of product
    about: str # Description of product
    url: str # URL to product purchasing site

class BasicSelection(BaseModel):
    csv_file: str # Link to csv file
    product_databse: list[Product] # list of products
    
    def parse_dataset(self):
        df = pd.read_csv(self.csv_file)
        for entry in df.rows:
            temp_product = Product(name = df.entry['Name'], 
                                   type = df.entry['Product Type'])
            self.product_database.append(temp_product)
    



