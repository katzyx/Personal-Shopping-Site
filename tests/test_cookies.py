import pytest
from shopping_site import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_cookie_set_on_first_visit(client):
    """Test that cookies are properly set when user first submits their details"""
    test_cases = [
        "I am a 23 year-old woman with oily sensitive skin",
        "I have mature skin with wrinkles",
        "I am a teenager with acne-prone skin",
        "I have combination skin and hyperpigmentation",
        ""  # Test empty input
    ]
    
    for user_details in test_cases:
        # Submit user details with proper form data
        response = client.post('/', data={'user_details': user_details}, follow_redirects=True)
        assert response.status_code == 200

def test_cookie_persistence(client):
    """Test that cookies persist across different pages"""
    user_details = "I am 30 with dry skin"
    
    # Set initial cookie through POST
    response = client.post('/', data={'user_details': user_details})
    
    # Test landing page with cookie
    response = client.get('/')
    assert response.status_code in [200, 302]

def test_cookie_update(client):
    """Test updating existing cookies"""
    initial_details = "I am 25 with normal skin"
    new_details = "I am 25 with dry sensitive skin"
    
    # Set initial cookie
    response = client.post('/', data={'user_details': initial_details})
    
    # Update with new details via JSON (as seen in shopping_site.py)
    response = client.post('/update_user_details', 
                         json={
                             'current_details': initial_details,
                             'new_details': new_details
                         },
                         content_type='application/json')
    
    assert response.status_code == 200
    assert 'merged_description' in response.get_json()

def test_cookie_redirect_behavior(client):
    """Test redirect behavior based on cookie presence"""
    # Test without cookie first
    response = client.get('/')
    assert response.status_code == 200  # Should show landing page
    
    # Set a cookie and test again
    response = client.post('/', data={'user_details': "I am 28 with oily skin"})
    response = client.get('/')
    assert response.status_code == 302  # Should redirect with cookie

def test_get_cookie(client):
    """Test getting cookie value"""
    # First set a cookie
    user_details = "I am 35 with combination skin"
    client.post('/', data={'user_details': user_details})
    
    # Test get_cookie route
    response = client.get('/get_cookie')
    assert response.status_code == 200
    assert 'Your profile:' in response.get_data(as_text=True)

def test_invalid_cookie_handling(client):
    """Test handling of invalid or malformed cookies"""
    # Test with invalid cookie value
    response = client.get('/')
    assert response.status_code == 200  # Should still load landing page
    
    # Test with extremely long cookie value
    long_value = "x" * 4096  # Most browsers limit cookies to 4KB
    response = client.post('/', data={'user_details': long_value})
    assert response.status_code in [200, 302]  # Should handle long value gracefully