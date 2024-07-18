# ignore for now
import sys
import requests
import json
import os
import openai
from openai import OpenAI
import shade_match
from shade_match import shade_finder

openai_api_key = " "
if openai_api_key is None:
    raise ValueError("OpenAI API key is not set in environment variables.")

client = OpenAI(
    # This is the default and can be omitted
    api_key=openai_api_key,
)

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

def chatgpt(colour):
    messages = [ {"role": "system", "content":"You are a helpful assistant. Give the rgb value for the colour specified by user only simply in the format r,g,b , without any words in the answer."} ]

    satisfied = True
    user_shade = ""
    col = colour
    if col:
        messages.append(
        {"role": "user", "content": col},
        )
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages
        )
        answer = chat.choices[0].message.content
        # print(f"ChatGPT: {answer}")
        messages.append({"role": "assistant", "content": answer})
    
    return answer

# if __name__ == "__main__":
#     colour = []
#     ans = chatgpt(colour)
#     x = ans.split(",")
#     y = (int(x[0]), int(x[1]), int(x[2]))
#     print(ans)
#     result = shade_finder(y)
#     print(result)

