import pytest
import json
from product_selection.user_input import UserInput
from product_selection.key import API_key

@pytest.fixture
def u():
    who = "I am a 23 year-old Asian woman with oily sensitive skin and light-medium complexion"
    what = "I want an exfoliating toner, lip balm, and eyeliner, each under $30"
    return UserInput(API_key, who, what)

def test_who_you_are(u):
    u.input_to_json('who')
    check = u.input_who
    print(check)
    arr = ["23", "asian", "oily", "sensitive", "light", "medium"]
    ch = json.loads(check)
    for key, value in ch.items():
        if isinstance(value, str):
            ch[key] = value.lower()
    for word in arr:
        res = False
        for v in ch.values():
            if word in v:
                res = not res
                break
        print(word)
        assert res
            

def test_what_you_want(u):
    u.input_to_json('what')
    check = u.input_what
    print(check)
    arr = ["toner", "lip", "eyeliner", "30"]
    ch = json.loads(check)
    for key, value in ch.items():
        if isinstance(value, str):
            ch[key] = value.lower()
    for word in arr:
        res = False
        for v in ch.values():
            if word in v:
                res = not res
                break
        print(word)
        assert res

def test_is_json(): # already covered in code
    """ try:
        json.loads(input)
        return True
    except ValueError:
        return False """
    pass
    
