'''
Description:
Authors: Floria Fang Zhang, Hope Hadfield, Katherine Zhang, Maisey Perelonia
'''

# Imports
from pydantic import BaseModel
import pandas
import csv

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






