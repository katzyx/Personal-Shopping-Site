from __init__ import Product, BasicSelection

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "ProductDataset.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()

    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    # print(select.user_info)
    products_selected = select.keyword_lookup()
    
    for product in products_selected:
        print(product.brand, product.name)
    


if __name__ == "__main__": 
    input_who = '{"Age":"21","Sex":"Female","Ethnicity":"Asian","Skin Tone":"Light Neutral"}'
    input_what = '{"Products":"Skincare products, Foundation","Price":"$20 to $60", "Formula":"Cream"}'
    basic_map(input_who, input_what)



