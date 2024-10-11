import openai # type: ignore
from product_selection.key import API_key

# For internal testing
# from key import API_key

class Blogpost:
    def __init__(self, openai_key, input_who, input_what):
        self.openai_key = openai_key
        self.input_who = input_who
        self.input_what = input_what


    def write_blogpost(self):
        openai.api_key = self.openai_key
        messages = [ {"role": "system", "content": "You are a personal beauty advisor and guide."} ]

        if self.input_who is None:
            self.input_who = "no input provided"
        if self.input_who is None:
            self.input_what = "no input provided"

        message = "Details about me: " + self.input_who + ". What I'm looking for: " + self.input_what + ". Given this information, write a paragraph (maximum 1200 characters) giving me personalized advice on what I should be looking for in products or on the application of these products without naming specific products or brands."
        messages.append({"role": "user", "content": message})        

        try:
            chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            reply = chat.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            reply = "{}"  # return an empty JSON if something goes wrong

        # print (reply)
        return reply
    

# blogpost = Blogpost(API_key, '{"Age": "21", "Sex": "Female", "Ethnicity": "Chinese"}', '{"Products": "Skincare, Foundation", "Price": "40"}')
# blogpost.write_blogpost()