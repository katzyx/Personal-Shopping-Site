import pytest
import time
from shopping_site import app
from product_selection.select_product import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_product_formatting(client):
    with app.app_context():
        # Set up session with very specific product request
        with client.session_transaction() as sess:
            sess['user_details'] = "I have normal skin"
            sess['product_preferences'] = "foundation"
    
        response = client.get('/index')
        rendered = response.data.decode()
        ex = '''<div class="loader"></div>'''
        assert ex in rendered

        time.sleep(60)

        response2 = client.get('/display_results')
        rendered2 = response2.data.decode()
        # Look for the product details within the product display structure
        print(rendered2)
        html0 = '''<div height="200em" style="margin-bottom: 3em;">
                <img src="https://www.sephora.com/productimages/sku/s2597276-main-zoom.jpg?imwidth=465" width="125em">
            </div>
            <p class="prod_name">Triclone Skin Tech Medium Coverage Foundation with Fermented Arnica</p>
            <p class="prod_brand">
                <b style="margin-top: 0.5em">HAUS LABS BY LADY GAGA</b>
            </p>'''

        html1 = '''<div style="flex: 14%; padding: 0.5em 0em">
          <div height="200em" style="margin-bottom: 3em;">
            <img src="https://www.sephora.com/productimages/sku/s1359694-main-zoom.jpg?imwidth=465" width="125em">
          </div>
          <p class="prod_name">Luminous Silk Perfect Glow Flawless Oil-Free Foundation</p>
          <p class="prod_brand">
            <b style="margin-top: 0.5em">Armani Beauty</b>
          </p>'''
        assert html0 in rendered2
        assert html1 in rendered2 

