from __init__ import Product, BasicSelection

def basic_map(user_who, user_what): 
    # Extract Database
    csv_path = "ProductDataset.csv"
    select = BasicSelection(csv_file=csv_path)
    select.parse_dataset()

    # Extract user info and use keyword lookup
    select.parse_user_jsons(user_who, user_what)
    select.keyword_lookup()


if __name__ == "__main__": 
    input_who = '{"Age":"21","Sex":"Female","Ethnicity":"Asian","Skin Tone":"Light Neutral"}'
    input_what = '{"Products":"Foundation","Price":"$20 to $60"}'
    basic_map(input_who, input_what)



