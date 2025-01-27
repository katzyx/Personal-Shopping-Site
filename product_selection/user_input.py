import openai # type: ignore
import json # type: ignore
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
        messages = [ {"role": "system", "content": "You are a personal beauty advisor! Ignore grammar errors. If fields from the example output are missing, do not include."} ]

        if type == 'who':
            raw_input = self.raw_input_who
        elif type == 'what':
            raw_input = self.raw_input_what
        else:
            raw_input = None
        
        if type == 'who':
            example_output = '\n\nEXAMPLE OUTPUT:{\"Age\":\"22\",\"Sex\":\"Female\",\"Skin Tone\":\"Olive\",\"Skin Type\":\"Oily\"}'
            message = "Extract user information (in JSON format - in one line) from the following string (for Products category, return a comma-separated string and use only singular nouns): " + raw_input + example_output
        elif type == 'what':
            example_output = '\n\nEXAMPLE OUTPUT:{\"Products\":\"Foundation\",\"Price\":\"40\",\"Brand\":\"Dior\",\"Colour\":\"Pink\"}'
            message = "Extract user information (in JSON format - in one line) from the following string. For Price, always return a specific number (if 'around X' is given, use X; if no price mentioned, use 50; if 'cheap' or 'affordable', use 25; if 'expensive' or 'high-end', use 100): " + raw_input + example_output
        else:
            example_output = ""
            message = ""

        # Add null check
        if raw_input is None:
            raw_input = "no input received"  # or some default value
        
        messages.append({"role": "system", "content": message})

        try:
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            reply = "{}"  # return an empty JSON if something goes wrong
        
        print(reply)

        # Add checks to see if output is correct
        while True:
            rerun = False
            message = ""

            # Check output is JSON
            try: 
                json.loads(reply)
            except Exception as e:
                print(f"Error returning JSON string: {e}")
                message += "Format this string into JSON (for Products category, return a comma-separated string and use only singular nouns)."
                rerun = True

            # Check if price is correct
            try:
                if 'Price' in reply:
                    if isinstance(reply, str):
                        data = json.loads(reply)
                    else:
                        data = reply 
                    price_list = data['Price']
                    min, max = price_list[0], price_list[1]
                    float(min) + float(max)
            except Exception as e:
                print(f"Error returning Price: {e}")
                message += "Change Price into a tuple of two valid numbers. If maximum price not specified, used 99999999"
                rerun = True
            
            if rerun:
                message += "Here is the string to change: " + reply
                messages.append({"role": "system", "content": message})
                try:
                    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                    reply = chat.choices[0].message.content
                except Exception as e:
                    print(f"Error during OpenAI API call: {e}")
                    reply = "{}"
            else:
                break
            
        # For debugging purposes
        print(reply)

        # debug and check if reply is empty or doesn't make sense

        if type == 'who':
            self.input_who = reply
        elif type == 'what':
            self.input_what = reply
        

    def parse_user_inputs(self):
        self.input_to_json('who')
        self.input_to_json('what')
    
     # combine current description with new description when user updates
    def merge_descriptions(self, current_desc, new_desc):
        openai.api_key = self.openai_key
        messages = [
            {"role": "system", "content": "You are an assistant that combines user descriptions about themselves for a beauty website. Merge the information intelligently, remove redundancies, and maintain a natural flow. Only include the information that the user has entered. Do not provide any additional information or descriptions. If you do not understand the user's input, return the current description."}
        ]

        message = f"""Current description: {current_desc}
        New information to add: {new_desc}
        Please combine these descriptions into a single, coherent paragraph that includes all relevant information without redundancy."""

        messages.append({"role": "user", "content": message})

        try:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.4
            )
            reply = chat.choices[0].message.content
            return reply
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            return current_desc + " " + new_desc  # fallback to simple concatenation
    

# user_input = UserInput(API_key, "I am a 21 year old Asian woman with light oily skin", "I am looking for foundation and skincare products under 40$")
# user_input.parse_user_inputs()