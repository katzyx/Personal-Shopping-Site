import csv
import math

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
def calculate_distance(rgb1, rgb2):
    return math.sqrt(sum((rgb1[i] - rgb2[i]) ** 2 for i in range(3)))

# calculating the distance between the product's RGB value and the defined shade rgb values
def categorize_rgb(rgb):
    min_distance = float('inf')
    closest_shade = "No shade match found"
    for shade, shade_rgb in shade_values.items():  # Iterate over shade_values
        distance = calculate_distance(rgb, shade_rgb)
        if distance < min_distance:
            min_distance = distance
            closest_shade = shade
    return closest_shade

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