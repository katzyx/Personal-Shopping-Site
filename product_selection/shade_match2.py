import csv
import pandas as pd

# define shade groups and their ranges
shade_ranges = {
    "Red": [(150, 0, 0), (255, 100, 100)],
    "Pink": [(255, 182, 193), (255, 192, 203)],
    "Purple": [(128, 0, 128), (160, 32, 240)],
    "Light": [(245, 228, 215), (214, 181, 153)],
    "Medium": [(199, 155, 122), (117, 73, 61)],
    "Dark": [(89, 58, 47), (44, 34, 30)],
}

# determinE if rgb value is within a range
def in_range(rgb, min, max):
    return all(min[i] <= rgb[i] <= max[i] for i in range(3))

# categorize rgb value
def categorize_rgb(rgb):
    for color, (min, max) in shade_ranges.items():
        if in_range(rgb, min, max):
            return color
    return "No shade match found"

# categorize shades in data
def categorize_products(file, product_shades):
    with open(file, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_name = row["Product Name"]
            rgb_values = (int(row["R"]), int(row["G"]), int(row["B"]))
            prod_shade = categorize_rgb(rgb_values)
            if prod_shade in product_shades:
                product_shades[prod_shade].append(product_name)
            else:
                product_shades[prod_shade] = [product_name]

# empty dictionary to store shade ranges
product_shades = {}

csv_path = "ShadeData.csv"
categorize_products(csv_path, product_shades)

# print products in shade ranges
for group, products in product_shades.items():
    print(f"{group.capitalize()} products:")
    for product in products:
        print(f"  - {product}")