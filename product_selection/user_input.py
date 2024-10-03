import openai # type: ignore
from product_selection.key import API_key

# For internal testing
# from key import API_key

class UserInput:
    def __init__(self, openai_key, raw_input_who, raw_input_what):
        self.openai_key = openai_key
        self.raw_input_who = raw_input_who
        self.raw_input_what = raw_input_what
        self.input_who = ''
        self.input_what = ''

    def input_to_json(self, type):
        openai.api_key = self.openai_key
        messages = [ {"role": "system", "content": "You are a personal beauty advisor! Ignore grammar errors. If fields are missing, do not include."} ]

        if type == 'who':
            raw_input = self.raw_input_who
            example_output = '\n\nEXAMPLE OUTPUT:{\"Age\":\"22\",\"Sex\":\"Female\",\"Skin Tone\":\"Olive\",\"Skin Type\":\"Oily\"}'
        elif type == 'what':
            raw_input = self.raw_input_what
            example_output = '\n\nEXAMPLE OUTPUT:{\"Products\":\"Foundation,Primers\",\"Price\":\"Under $100\",\"Brand\":\"Dior\"}'

        if raw_input == None:
            raw_input = "no input received"

        message = "Extract user information (in JSON format - in one line) from the following string: " + raw_input + example_output
        messages.append({"role": "system", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = chat.choices[0].message.content

        # print (reply)
        if type == 'who':
            self.input_who = reply
        elif type == 'what':
            self.input_what = reply
        

    def parse_user_inputs(self):
        self.input_to_json('who')
        self.input_to_json('what')
    
    # Code moved here from map_user_to_product.py - currently not needed (open ai returns correct json format)
    '''
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
    '''

# user_input = UserInput(API_key, "I am a 21 year old Asian woman with light oily skin", "I am looking for foundation and skincare products under 40$")
# user_input.parse_user_inputs()