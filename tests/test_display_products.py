import pytest
from shopping_site import app
from product_selection.select_product import Product

# test cases
VALID_PRODUCTS = [
    Product(
        name="RadiantGlow Foundation",
        type="Foundation",
        brand="Luminous Beauty",
        color=["Light Ivory"],
        price=45,
        size="30ml",
        formula="Liquid",
        ingredients=["Water", "Glycerin"],
        about="radiant",
        url="https://lh3.googleusercontent.com/pw/AP1GczMKf0c1qLDV3wI6kevBeNQHQOBmUim-UM0u9S7gK5QfCkg6pZTpy1uoMU_cWpsd70_WPaovwVfGzucinVby2bFWnm5TOCvGHiZQptXi8rtSoPIkJKlA-i4rDCsUVTXUuN3VmjToLpQzEqK3M-nlaEza=w609-h913-s-no-gm?authuser=1"
    )
]

INVALID_PRODUCTS = [
    [],  # Empty product list
    None,  # None value
    [Product(  # Invalid product with missing required fields
        name="",
        type="",
        brand="",
        color=[],
        price=None,
        size="",
        formula="",
        ingredients=[],
        about="",
        url=""
    )]
]

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_products(client):
    """Test that valid products are displayed correctly"""
    with app.app_context():
        # Set up session with very specific product request
        with client.session_transaction() as sess:
            sess['user_details'] = "I want the RadiantGlow Foundation from Luminous Beauty"
            sess['product_preferences'] = "RadiantGlow Foundation"
        
        response = client.get('/index')
        rendered = response.data.decode()
        
        # Look for the product details within the product display structure
        expected_product_html = f'''<div style="flex: 14%; padding: 0.5em 0em">
          <img src="{VALID_PRODUCTS[0].url}" height="200em" width="125em">
          <p>RadiantGlow Foundation</p>
          <b style="margin-top: 0.5em">Luminous Beauty</b>
          <p style="margin-top: 0.5em">$45</p>'''
        
        assert expected_product_html in rendered

# def test_invalid_products(client):
#     """Test handling of invalid product data"""
#     with app.app_context():
#         # Test case where user asks for a product that doesn't exist
#         with client.session_transaction() as sess:
#             sess['user_details'] = "I want a magical foundation that turns me into a unicorn"
#             sess['product_preferences'] = "Unicorn Magic Foundation"
        
#         response = client.get('/index')
#         rendered = response.data.decode()
        
#         # Verify the error message and image are displayed
#         assert 'Sorry, your search did not return any products.' in rendered
#         assert 'nothing_found.png' in rendered
        
#         # Verify no product elements are displayed
#         assert '<div style="flex: 14%; padding: 0.5em 0em">' not in rendered
#         assert 'ADD TO BAG' not in rendered

def test_edge_cases(client):
    """Test product recommendations for edge cases"""
    test_cases = [
        {
            'user_details': "I am 0 years old and need foundation",
            'preferences': "foundation for my skin",
            'expected_elements': ['foundation', 'skin', 'gentle']
        },
        {
            'user_details': "I am 100 years old with very dry mature skin",
            'preferences': "hydrating foundation",
            'expected_elements': ['hydrating', 'moisturizing', 'anti-aging']
        },
        {
            'user_details': "I have very dark skin tone and need foundation",
            'preferences': "foundation for dark skin",
            'expected_elements': ['deep', 'dark', 'melanin']
        },
        {
            'user_details': "I have extremely sensitive skin with eczema",
            'preferences': "gentle foundation",
            'expected_elements': ['sensitive', 'hypoallergenic', 'gentle']
        }
    ]

    with app.app_context():
        for case in test_cases:
            # Set up session for each test case
            with client.session_transaction() as sess:
                sess['user_details'] = case['user_details']
                sess['product_preferences'] = case['preferences']
            
            response = client.get('/index')
            rendered = response.data.decode()
            
            # Verify that products are displayed (system doesn't crash)
            assert '<div style="flex: 14%; padding: 0.5em 0em">' in rendered
            assert 'ADD TO BAG' in rendered
            
            # Check that at least some products are shown
            assert '<img src=' in rendered
            assert '<p>' in rendered
            
            # Check that the blog post contains relevant advice
            assert any(element.lower() in rendered.lower() for element in case['expected_elements']), \
                f"Expected to find relevant advice for case: {case['user_details']}"
            
            # Verify price information is displayed
            assert '$' in rendered