# Imports
import pandas as pd # type: ignore
import numpy as np # type: ignore
import json
import re
from pydantic import BaseModel # type: ignore

class Shade(BaseModel):
    name: str # Shade name
    descriptor: str # Descriptor of Shade
    image_url: str # URL to image
    product_url: str # URL to product purchase

class Review(BaseModel):
    title: str # Review title
    rating: int # Star rating
    shade_purchased: str # Name of shade purchased
    buyer_description: str # Physical description of buyer (eye / hair / skin color, skin type, ...)
    review: str # Review left by buyer

class Product(BaseModel): 
    name: str # Product name
    type: str # Product type
    shades: list[Shade] # List of all product shades
    price: float # Price of product in CAD
    size: str # Product size
    about: str # Description of product
    ingredients: str # Ingredients of product
    how_to_use: str # Instructions on use
    reviews: list[Review] # List of all buyer reviews


    def get_attribute(self, entry):
        if entry == 'Products': return self.type
        if entry == 'Brand': return self.brand
        if entry == 'Price': return self.price
        if entry == 'Formula': return self.formula