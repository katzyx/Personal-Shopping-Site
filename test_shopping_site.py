import pytest
from shopping_site import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_cookies(client):
    pass
