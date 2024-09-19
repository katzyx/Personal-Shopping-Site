import openai
from key import API_key

class Blogpost:
    def __init__(self, openai_key, input_who, input_what):
        self.openai_key = openai_key
        self.input_who = input_who
        self.input_what = input_what


    def write_blogpost(self):
        openai.api_key = self.openai_key
        messages = [ {"role": "system", "content": "You are a personal beauty advisor and guide."} ]

        message = "Details about me: " + self.input_who + ". What I'm looking for: " + self.input_what + ". Given this information, write a paragraph giving me personalized advice on what I should be looking for in products or on application the application of these products without naming specific products or brands."
        messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        reply = chat.choices[0].message.content

        print (reply)
        return reply
    

# blogpost = Blogpost(API_key, '{"Age": "21", "Sex": "Female", "Ethnicity": "Chinese"}', '{"Products": "Skincare, Foundation", "Price": "40"}')
# blogpost.write_blogpost()