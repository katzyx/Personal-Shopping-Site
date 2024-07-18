import sys
import json
from select_product import Product, BasicSelection


def format_input_into_json(php_input):
    input_string = php_input.strip('{}')
    items = input_string.split(',')

    data = {}
    key = ''
    for item in items:
        # Split each item into key and value (if there's an ':' sign)
        parts = item.split(':')
        
        if len(parts) > 1:
            key = parts[0].strip()
            value = parts[1].strip()
            data[key] = value
        else:
            # If no '=', add it to previous key
            data[key] += ', ' + parts[0].strip()

    # Step 2: Convert dictionary to JSON string
    json_string = json.dumps(data)

    return json_string

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "ProductDataset.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()

    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    products_selected = select.keyword_lookup()
    
    # Provide top 3 recommended products to user
    for product in products_selected:
        print(product.brand, product.name)
    

# Uses JSON strings from GPT
if __name__ == "__main__": 
    sys.argv = ['map_user_to_product.py', '.{Age:21,Sex:Female,Ethnicity:Chinese}', '.{Products:Foundation,Price:under50}']

    input_who = format_input_into_json(sys.argv[1].replace('.',''))
    input_what = format_input_into_json(sys.argv[2].replace('.',''))
    
    basic_map(input_who, input_what)



