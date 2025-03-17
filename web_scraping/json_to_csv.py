import json
import os


def json_to_csv(json_file_path, csv_file_path, product_id):
    # check if csv file exists
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'x') as csv:
            header = 'id,name,brand,categories,price,shades,about,ingredients,how_to_use,rating,number_of_reviews,product_url,image_url\n'
            csv.write(header)
    
    try:
        with open(json_file_path, 'r') as file:
            product = json.load(file)  # Load the JSON data
            # Extract key fields into a plain-text document
        
        with open(csv_file_path, 'a') as csv:
            to_write = (f"{product['product_id']},\"{product['name']}\",\"{product['brand']}\",\"{product['categories']}\",{product['price']},")
            
            shades_list = '\"'
            for shade in product['shades']:
                shades_list += shade['shade_name'] + ' - ' + shade['shade_descriptor'] + ', '
            shades_list += '\"'

            to_write += (f"{shades_list},\"{product['about']}\",\"{product['ingredients']}\",\"{product['how_to_use']}\",")
            to_write += (f"{product['overall_rating']},{product['num_reviews']},{product['product_url']},{product['image_url']}\n")
            csv.write(to_write)

    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found.")
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__": 
    csv_filename = '/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products.csv'
    for count in range(1, 1797):
        json_filename = "/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products_json/product_id_" + str(count) + ".json"
        json_to_csv(json_filename,csv_filename, count)
