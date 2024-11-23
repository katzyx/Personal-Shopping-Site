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

    def __str__(self) -> str:
        output = []
        output.append(f"Shade Name: {self.name}")
        output.append(f"Descriptor: {self.descriptor}")
        output.append(f"Image URL: {self.image_url}")
        
        return "\n".join(output)

class Review(BaseModel):
    title: str # Review title
    rating: int # Star rating
    shade_purchased: str # Name of shade purchased
    buyer_description: str # Physical description of buyer (eye / hair / skin color, skin type, ...)
    review: str # Review left by buyer

class Product(BaseModel): 
    id: int = None # Product ID
    name: str = '' # Product name
    brand: str = '' # Product brand
    categories: list[str] = [] # Product cateogories
    shades: list[Shade] = [] # List of all product shades
    price: float = None # Price of product in CAD
    size: str = '' # Product size
    about: str = '' # Description of product
    ingredients: str = '' # Ingredients of product
    how_to_use: str = '' # Instructions on use
    reviews: list[Review] = [] # List of all buyer reviews


    def get_attribute(self, entry):
        if entry == 'Products': return self.type
        if entry == 'Brand': return self.brand
        if entry == 'Price': return self.price
        if entry == 'Formula': return self.formula

    
    def __str__(self) -> str:
        output = []
        output.append(f"Product Name: {self.name}")
        output.append(f"Brand: {self.brand}")
        output.append(f"Categories: {', '.join(self.categories)}")
        output.append(f"Number of Shades: {len(self.shades)}")
        output.append(f"Price: ${self.price:.2f} CAD" if self.price else "Price: Not available")
        output.append(f"Size: {self.size}")
        output.append(f"About: {self.about}")
        output.append(f"Ingredients: {self.ingredients}")
        output.append(f"How to Use: {self.how_to_use}")
        output.append(f"Number of Reviews: {len(self.reviews)}")
        
        return "\n".join(output)