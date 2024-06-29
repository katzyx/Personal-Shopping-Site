import csv
import math
from pydantic import BaseModel

class ShadeMatch(BaseModel):
    # define shade groups and their ranges
    shade_values = {
        "Red": (255, 0, 0),
        "Pink": (255, 192, 203),
        "Purple": (128, 0, 128),
        "Light": (245, 228, 215),
        "Medium": (199, 155, 122),
        "Dark": (89, 58, 47),
    }
    # calculate distance between two rgb values
    def calculate_distance(self, rgb1, rgb2):
        return math.sqrt(sum((rgb1[i] - rgb2[i]) ** 2 for i in range(3)))

    # calculating the distance between the product's RGB value and the defined shade rgb values
    def categorize_rgb(self, rgb):
        min_distance = float('inf')
        closest_shade = "No shade match found"
        for shade, shade_rgb in self.shade_values.items():  # Iterate over shade_values
            distance = self.calculate_distance(rgb, shade_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_shade = shade
        return closest_shade

    # find products that are closest to the given shade
    def find_closest_products(self, user_shade, product_shades):
        if user_shade not in shade_values:
            return "Shade not found in predefined shades."

        rgb_val = shade_values[user_shade] 
        closest_products = []
        min_distance = float('inf')

        for shade, products in product_shades.items():
            for rgb, product_name, shade_name in products:
                distance = self.calculate_distance(rgb, rgb_val)
                if distance < min_distance:
                    closest_products = [(product_name, shade_name, shade)]
                    min_distance = distance
                elif distance == min_distance:
                    closest_products.append((product_name, shade_name, shade))

        # return tuple of products
        return closest_products

    # categorize shades in data
    def categorize_products(self, file, product_shades):
        with open(file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                product_name = row["Product Name"]
                shade_name = row["Shade Name"]
                rgb_values = (int(row["R"]), int(row["G"]), int(row["B"]))
                prod_shade = self.categorize_rgb(rgb_values)

                # store rgb value and product name in dictionary
                if prod_shade in product_shades:
                    product_shades[prod_shade].append((rgb_values, product_name, shade_name))
                else:
                    product_shades[prod_shade] = [(rgb_values, product_name, shade_name)]


    def find_shade(self):
        # empty dictionary to store shade ranges
        product_shades = {}

        csv_path = "ShadeData.csv"
        self.categorize_products(csv_path, product_shades)

        # # print products in shade ranges
        # for group, products in product_shades.items():
        #     print(f"{group.capitalize()} products:")
        #     for product in products:
        #         print(f"  - {product}")

        # get user input and find the closest product(s)
        user_shade = input("Shade wanted: ").capitalize()
        closest_products = self.find_closest_products(user_shade, product_shades)

        # if the result is a string, then product was not found
        if isinstance(closest_products, str):
            print(closest_products)
        # else product(s) found
        else:
            print(f"Closest product(s) to {user_shade}:")
            for product_name, shade_name, shade in closest_products:
                print(f"  - {product_name} in shade {shade_name}")

        # return closest_products

