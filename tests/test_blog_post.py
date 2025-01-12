import pytest
from shopping_site import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_blog_post_content(client):
    """Test that blog posts contain relevant information based on user details"""
    test_cases = [
        {
            'user_details': "I am 25 with oily skin and acne concerns",
            'preferences': "foundation for oily skin",
            'expected_content': ['oil', 'acne', 'control', 'matt'],
            'unexpected_content': ['wrinkle', 'dry skin', 'anti-aging']
        },
        {
            'user_details': "I am 60 with mature dry skin",
            'preferences': "hydrating foundation",
            'expected_content': ['hydrat', 'moistur', 'mature'],
            'unexpected_content': ['acne', 'oil control', 'teen']
        },
        {
            'user_details': "I have sensitive skin and rosacea",
            'preferences': "gentle foundation",
            'expected_content': ['sensitive', 'gentle', 'sooth'],
            'unexpected_content': ['exfoliat']
        },
        {
            'user_details': "I am looking for clean beauty products",
            'preferences': "clean foundation ingredients",
            'expected_content': ['clean', 'natural', 'ingredient'],
            'unexpected_content': ['metal']
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
            
            # Extract blog post content
            blog_start = rendered.find('<legend>From your beauty advisor</legend>')
            blog_end = rendered.find('</fieldset>', blog_start)
            blog_content = rendered[blog_start:blog_end].lower()
            
            # Test for expected content
            for term in case['expected_content']:
                assert term.lower() in blog_content, \
                    f"Expected to find '{term}' in blog post for case: {case['user_details']}"
            
            # Test for unexpected content
            for term in case['unexpected_content']:
                assert term.lower() not in blog_content, \
                    f"Found unexpected term '{term}' in blog post for case: {case['user_details']}"

def test_blog_post_personalization(client):
    """Test that blog posts are personalized based on user details"""
    # Test same preference with different user details
    test_pairs = [
        {
            'case1': {
                'user_details': "I am 20 with oily skin",
                'preferences': "foundation"
            },
            'case2': {
                'user_details': "I am 50 with dry skin",
                'preferences': "foundation"
            }
        },
        {
            'case1': {
                'user_details': "I have fair sensitive skin",
                'preferences': "coverage foundation"
            },
            'case2': {
                'user_details': "I have dark skin with hyperpigmentation",
                'preferences': "coverage foundation"
            }
        }
    ]

    with app.app_context():
        for pair in test_pairs:
            # Get blog posts for both cases
            blogs = []
            for case in [pair['case1'], pair['case2']]:
                with client.session_transaction() as sess:
                    sess['user_details'] = case['user_details']
                    sess['product_preferences'] = case['preferences']
                
                response = client.get('/index')
                rendered = response.data.decode()
                
                # Extract blog content
                blog_start = rendered.find('<legend>From your beauty advisor</legend>')
                blog_end = rendered.find('</fieldset>', blog_start)
                blogs.append(rendered[blog_start:blog_end])
            
            # Verify blogs are different despite same preference
            assert blogs[0] != blogs[1], \
                "Blog posts should be different for different user details"