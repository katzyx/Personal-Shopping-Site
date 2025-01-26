import pytest
import os
from shopping_site import app, getting_products, results_storage
from product_selection.select_product import Product, BasicSelection
import json

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

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment with correct working directory"""
    # Store original working directory
    original_dir = os.getcwd()
    
    # Change to project root directory (one level up from tests)
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    yield
    
    # Restore original working directory
    os.chdir(original_dir)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_products(client):
    """Test that valid products are displayed correctly"""
    with app.app_context():
        # Set up session
        user_details = "I want the RadiantGlow Foundation from Luminous Beauty"
        product_preferences = "RadiantGlow Foundation"
        
        with client.session_transaction() as sess:
            sess['user_details'] = user_details
            sess['product_preferences'] = product_preferences
        
        # Generate products and store results
        getting_products(user_details, product_preferences)
        
        # Now get the display page
        response = client.get('/display_results')
        rendered = response.data.decode()
        
        # Basic assertions to verify the page loaded
        assert '<div style="flex: 14%; padding: 0.5em 0em">' in rendered
        assert 'ADD TO BAG' in rendered

def test_user_edge_cases(client):
    """Test product recommendations for edge cases where the user may have unique personal traits or rare product requsts"""
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
            # Set up session
            with client.session_transaction() as sess:
                sess['user_details'] = case['user_details']
                sess['product_preferences'] = case['preferences']
            
            # Generate products and store results
            getting_products(case['user_details'], case['preferences'])
            
            response = client.get('/display_results')
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

def test_sidebar_update(client):
    """Test that submitting the user details in the side bar updates the user's information"""
    with app.app_context():
        # Initial user details
        initial_details = "I am 25 with combination skin"
        product_preferences = "foundation"
        
        # Set up initial session
        with client.session_transaction() as sess:
            sess['user_details'] = initial_details
            sess['product_preferences'] = product_preferences
        
        # Generate initial products and store results
        getting_products(initial_details, product_preferences)
        
        response = client.get('/display_results')
        rendered = response.data.decode()
        
        # Verify initial user details are displayed
        assert initial_details in rendered
        
        # Simulate form submission with new details
        response = client.post('/update_user_details', 
            json={
                'current_details': initial_details,
                'new_details': "I have sensitive skin and need gentle products"
            },
            follow_redirects=True
        )
        
        # Verify response is JSON and contains merged description
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'merged_description' in data
        
        # Get updated page
        response = client.get('/display_results')
        rendered = response.data.decode()
        
        # Verify new details are present
        assert 'sensitive' in rendered.lower()
        assert 'gentle' in rendered.lower()
        
        # Verify old details are not completely lost (should be merged)
        assert '25' in rendered
        
        # Check that the blog post is updated to reflect new user details
        blog_start = rendered.find('<legend>From your beauty advisor</legend>')
        blog_end = rendered.find('</fieldset>', blog_start)
        blog_content = rendered[blog_start:blog_end].lower()
        
        assert 'sensitive' in blog_content
        assert 'gentle' in blog_content