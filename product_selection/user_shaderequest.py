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
    messages = [ {"role": "system", "content":"You are a helpful assistant. Give the rgb value for the colour specified by user, the overarching colour (e.g. red, pink, orange, purple, etc.), and attach a photo of the shade; use the same website for all photos. Ignore grammar mistakes."} ]

    satisfied = True
    user_shade = ""
    while satisfied:
        col = input("Enter the colour you'd like: ")
        if col:
            messages.append(
            {"role": "user", "content": col},
            )
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            answer = chat.choices[0].message.content
            print(f"ChatGPT: {answer}")
            messages.append({"role": "assistant", "content": answer})
        set = input("Are you satisfied? (y/n): ")

        if(set[0] == 'y'):
            satisfied = False
            user_shade = answer

    prompt = [ {"role": "system", "content":"You are a helpful assistant. Give the rgb value for the colour specified by user only simply in the format r,g,b , without any words in the answer."} ]    
    prompt.append(
    {"role": "user", "content": user_shade},
    )
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=prompt
    )
    answer = chat.choices[0].message.content
    prompt.append({"role": "assistant", "content": answer})

    colour_convert = [ {"role": "system", "content":"You are a helpful assistant. In a one-word answer, give the overarching colour with first letter capitalized."} ]    
    colour_convert.append(
    {"role": "user", "content": user_shade},
    )
    chat = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=colour_convert
    )
    answer2 = chat.choices[0].message.content
    colour_convert.append({"role": "assistant", "content": answer2})
    colour.append(answer2)
    
    return answer

if __name__ == "__main__":
    colour = []
    ans = chatgpt(colour)
    x = ans.split(",")
    y = (int(x[0]), int(x[1]), int(x[2]))
    print(colour)
    result = shade_finder(colour[0], y)
    print(result)

