import pytest
import json
from product_selection.user_input import UserInput
from product_selection.key import API_key
from shopping_site import app
from flask import Flask, session, request, redirect, url_for

@pytest.fixture
def arr_who():
    return ["60", "sun", "spot", "wrinkle"]

@pytest.fixture
def arr_what():
    return ["serum", "pigment", "mineral", "sun"]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Fixture for testing UserInput class methods
@pytest.fixture
def user_input_instance():
    who = "I am 60 year old woman with sun spots and wrinkles"
    what = "I want a serum that fades hyperpigmentation and a mineral sunscreen, I don't have a price range"
    return UserInput(API_key, who, what)

def test_input_to_json(user_input_instance):
    """Test that user inputs are correctly converted to JSON"""
    # Test who input
    user_input_instance.input_to_json('who')
    who_json = user_input_instance.input_who.lower()  # Convert to lowercase for comparison
    assert "60" in who_json
    assert "sun spot" in who_json.lower()
    assert "wrinkle" in who_json.lower()
    
    # Test what input
    user_input_instance.input_to_json('what')
    what_json = user_input_instance.input_what.lower()  # Convert to lowercase for comparison
    assert "serum" in what_json
    assert "hyperpigmentation" in what_json
    assert "mineral" in what_json
    assert "sunscreen" in what_json

def test_landing_who_inputs(client):
    """Test various user descriptions on landing who page"""
    test_cases = [
        "I am a 23 year-old Asian woman with oily sensitive skin and light-medium complexion",
        "I am teenager with dry lips",
        "I am teenager with eczema and acne",
        "I am a college student with oily skin and a damaged skin barrier",
        "I am 60 year old woman with sun spots and wrinkles",
        "",  # Empty input
        "I have sensitive skin"  # Minimal input
    ]
    
    for user_details in test_cases:
        # Submit user details
        response = client.post('/', data={'user_details': user_details})
        assert response.status_code == 302  # Should redirect
        assert response.location == url_for('landing_what')
        
        # Test that the cookie was set by making another request
        response = client.get('/')
        assert response.status_code == 302  # Should redirect if cookie exists

def test_landing_what_inputs(client):
    """Test various product preferences on landing what page"""
    test_cases = [
        {
            'user_details': "I am 23 with sensitive skin",
            'preferences': "I want an exfoliating toner, lip balm, and eyeliner, each under $30"
        },
        {
            'user_details': "I am teenager with dry lips",
            'preferences': "I want a high-shine lip gloss"
        },
        {
            'user_details': "I have acne prone skin",
            'preferences': "I want a gentle cleanser and retinoid"
        },
        {
            'user_details': "I have combination skin",
            'preferences': ""  # Empty preference
        }
    ]
    
    for case in test_cases:
        # Set user details through POST request
        client.post('/', data={'user_details': case['user_details']})
        
        response = client.post('/landing_what', data={
            'product_preferences': case['preferences']
        })
        assert response.status_code == 302
        assert response.location == url_for('index')
        
        # Check session storage for preferences
        with client.session_transaction() as sess:
            assert sess.get('product_preferences') == case['preferences']

def test_index_search_bar(client):
    """Test search bar functionality on index page"""
    test_cases = [
        {
            'initial_prefs': "I want foundation",
            'updated_prefs': "I am looking for a light foundation for sensitive skin",
            'user_details': "I have sensitive skin"
        },
        {
            'initial_prefs': "I want moisturizer",
            'updated_prefs': "I want a moisturizer with SPF",
            'user_details': "I have dry skin"
        },
        {
            'initial_prefs': "I want lipstick",
            'updated_prefs': "",  # Empty update
            'user_details': "I have normal skin"
        }
    ]
    
    for case in test_cases:
        # Set up initial state
        client.post('/', data={'user_details': case['user_details']})
        with client.session_transaction() as sess:
            sess.clear()
            sess['product_preferences'] = case['initial_prefs']
        
        # Test search bar update
        response = client.post('/index', data={
            'updated_preferences': case['updated_prefs']
        })
        assert response.status_code == 302
        assert response.location == url_for('index')
        
        # Check session storage updated
        with client.session_transaction() as sess:
            if case['updated_prefs']:  # If not empty
                assert sess.get('product_preferences') == case['updated_prefs']
            else:  # If empty, session is cleared
                assert sess.get('product_preferences') == ''  # Expect empty string instead of original value

def test_input_validation(client):
    """Test input validation and edge cases"""
    test_cases = [
        {'page': '/', 'data': {'user_details': 'x' * 1000}},  # Very long input
        {'page': '/landing_what', 'data': {'product_preferences': '<script>alert("xss")</script>'}},  # XSS attempt
        {'page': '/index', 'data': {'updated_preferences': None}},  # None value
        {'page': '/', 'data': {}},  # Missing data
        {'page': '/landing_what', 'data': {'product_preferences': ' '}},  # Whitespace only
    ]
    
    for case in test_cases:
        response = client.post(case['page'], data=case['data'])
        assert response.status_code in [200, 302]  # Should handle gracefully


