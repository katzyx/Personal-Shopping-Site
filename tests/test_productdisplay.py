from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pytest
import time
from shopping_site import app
from product_selection.select_product import Product
import tempfile
from shopping_site import getting_products

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
def poll_for_status(client, expected_status, timeout, interval):
    """
    Poll the `/check_status` endpoint until the expected status is reached.
    
    :param client: The Flask test client.
    :param expected_status: The status you want to wait for (e.g., 'done').
    :param timeout: Maximum time (in seconds) to wait for the status.
    :param interval: Time between each poll (in seconds).
    :return: True if the status was reached within the timeout, otherwise False.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        # Poll the status
        response = client.get('/check_status')
        data = response.json
        if data['status'] == expected_status:
            return True  # Status is 'done'

        time.sleep(interval)  # Wait for the next check

    return False  # Timeout reached, status was not 'done'

def test_product_formatting(client):
    with app.app_context():
        # Set up session with very specific product request
        with client.session_transaction() as sess:
            sess['user_details'] = "I have normal skin"
            sess['product_preferences'] = "foundation"
    
        # ex = '''<div class="loader"></div>'''
        # assert ex in rendered
        getting_products("I have normal skin", "foundation")
        task_done = poll_for_status(client, 'done', timeout=100, interval=1)

        assert task_done, "Task did not complete in time"

        response2 = client.get('/display_results')
        html_content = response2.data.decode()
        assert response2.status_code == 200

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_file:
            temp_file = tmp_file.name
            tmp_file.write(html_content.encode())  # Write the HTML content
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless if you don't need the UI
        chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/13.1 Safari/537.36')  # macOS Safari user agent

        # Initialize ChromeDriver with the emulated Safari macOS user agent
        driver = webdriver.Chrome(options=chrome_options)

        
        driver.get(f"file://{temp_file}")  # Load the HTML file in the browser

        try:
            # Wait for all <div> elements to load
            wait = WebDriverWait(driver, 100)  # Wait up to 40 seconds
            divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product_div")))

            # Check if all <div> elements have the same dimensions
            first_div = divs[0]  # Use the first <div> as the reference
            expected_width = first_div.size['width']
            expected_height = first_div.size['height']

            for index, div in enumerate(divs, start=1):
                width = div.size['width']
                height = div.size['height']
                print(f"Div #{index}: width={width}, height={height}")
                assert width == expected_width, f"Div #{index} has width {width}px, expected {expected_width}px"
                assert height == expected_height, f"Div #{index} has height {height}px, expected {expected_height}px"

        finally:
            time.sleep(30)
            driver.quit()
