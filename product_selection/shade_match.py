import csv
import pandas as pd
import math

def categorize_products(file, product_shades):
    with open(file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_name = row["Product Name"]
            rgb_values = (int(row["R"]), int(row["G"]), int(row["B"]))
            prod_shade_name = row["Shade Name"]
            prod_shade = row["Colour"]
            if prod_shade in product_shades:
                product_shades[prod_shade].append((rgb_values, product_name, prod_shade_name))
            else:
                product_shades[prod_shade] = [(rgb_values, product_name, prod_shade_name)]


product_shades = {}

def shade_finder(user_colour, user_shade):
    search = product_shades[user_colour]
    rgb_val = user_shade
 
     # find rgb value of the given shade in dict

     # ask chat gpt to convert shade to rgb value

     # value: 255, 192, 203 -- #FFC0CB 

     # find product closest to rgb value using algo
    distance = 10000
    answer = ""

    for p in search:
        current = math.sqrt((rgb_val[0] - p[0][0])**2 + (rgb_val[1] - p[0][1])**2 + (rgb_val[2] - p[0][2])**2)
        if current < distance:
            answer = p
            distance = current

    return answer[1]+ " in shade: " + answer[2]


csv_path = "ShadeData.csv"
categorize_products(csv_path, product_shades)

""" print(type(product_shades))
for group, products in product_shades.items():
    print(f"{group.capitalize()} products:")
    for product in products:
        print(f"  - {product}") """
