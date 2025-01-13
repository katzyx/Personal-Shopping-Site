import pytest
import json
from product_selection.user_input import UserInput
from product_selection.key import API_key

@pytest.fixture
def u():
    who = "I am 60 year old woman with sun spots and wrinkles"
    what = "I want a serum that fades hyperpigmentation and a mineral sunscreen, I don't have a price range"
    return UserInput(API_key, who, what)

@pytest.fixture
def arr_who():
    return ["60", "sun", "spot", "wrinkle"]

@pytest.fixture
def arr_what():
    return ["serum", "pigment", "mineral", "sun"]

def test_who_you_are(u, arr_who):
    u.input_to_json('who')
    check = u.input_who
    print(check)
    # assert False
    ch = json.loads(check)
    for key, value in ch.items():
        if isinstance(value, str):
            ch[key] = value.lower()
    for word in arr_who:
        res = False
        for v in ch.values():
            if word in v:
                res = True
                break
        print(word)
        assert res
            

def test_what_you_want(u, arr_what):
    u.input_to_json('what')
    check = u.input_what
    print(check)
    # assert False
    ch = json.loads(check)
    for key, value in ch.items():
        if isinstance(value, str):
            ch[key] = value.lower()
    for word in arr_what:
        res = False
        for v in ch.values():
            if word in v:
                res = True
                break
        print(word)
        assert res # mostly correct but test is having issues with lists in price ranges

def test_is_json(): # already covered in code
    """ try:
        json.loads(input)
        return True
    except ValueError:
        return False """
    pass
    
