import sys
# from select_product import Product, BasicSelection

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
    # input_who = '{"Age":"21","Sex":"Female","Ethnicity":"Asian","Skin Tone":"Light Neutral"}'
    # input_what = '{"Products":"Skincare products, Foundation","Price":"$20 to $60", "Formula":"Cream"}'

    json_input = ''
    for word in sys.argv[1:]:
        json_input += word + ' '
    print(json_input)

    input_who = json_input[json_input.find('{') : json_input.find('}') + 1]
    input_what = json_input[json_input.rfind('{') : json_input.rfind('}') + 1]

    basic_map(input_who, input_what)



