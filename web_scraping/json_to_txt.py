import json
import os


def json_to_txt(json_file_path, product_id):
    try:
        with open(json_file_path, 'r') as file:
            product = json.load(file)  # Load the JSON data
            # Extract key fields into a plain-text document
        
        text_file_path = "/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products_txt/product_id_" + str(count) + ".txt"
        with open(text_file_path, 'x') as file:
            file.write(f"Product ID: {product['product_id']}\n")
            file.write(f"Product Name: {product['name']}\n")
            file.write(f"Brand: {product['brand']}\n")
            file.write(f"Categories: {product['categories']}\n")
            file.write(f"Price: ${product['price']}\n")
            file.write(f"About: {product['about']}\n")
            file.write(f"Ingredients: {product['ingredients']}\n")
            file.write(f"How to Use: {product['how_to_use']}\n")
            file.write(f"Rating: {product['overall_rating']} stars\n")
            file.write(f"Number of Reviews: {product['num_reviews']}\n")
            file.write(f"Product URL: {product['product_url']}\n")
            file.write(f"Image URL: {product['image_url']}\n")
            
            file.write(f"\nShades: ")
            for shade in product['shades']:
                to_write = '\n - '
                to_write += 'Shade: ' + shade['shade_name']
                to_write += '\n   Shade Description: ' + shade['shade_descriptor']
                to_write += '\n   Shade Image URL: ' + shade['shade_image_url']
                file.write(to_write)
            
            # file.write(f"\n\nReviews: ")
            # for review in product['reviews']:
            #     to_write = '\n - '
            #     to_write += 'Title: ' + review['review_title']
            #     to_write += '\n   Rating (Out of 5): ' + str(review['review_rating'])
            #     to_write += '\n   Shade Purchased: ' + review['review_shade_purchased']
            #     to_write += '\n   Buyer Description: ' + review['review_buyer_description']
            #     to_write += '\n   Review: ' + review['review_text']
            #     file.write(to_write)


    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__": 
    for count in range(1, 1797):
        filename = "/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products_json/product_id_" + str(count) + ".json"
        print(filename)
        json_to_txt(filename, count)
