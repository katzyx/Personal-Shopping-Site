import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from pydantic import BaseModel # type: ignore
from product_info import Product, Shade, Review
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.common.exceptions import TimeoutException # type: ignore
import time


SEPHORA_URL: str = "https://www.sephora.com/ca/en/"
USER_AGENT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

class SephoraScraper(BaseModel):
    product_database: list[Product] # Database of all products
    brand_urls_list: list[str] = [] # List of brand urls
    product_urls_list: list[str] = [] # List of product urls
    product_id_counter: int = 1 # Product ID Tracker

    def write_to_file(self, filename, info):
        with open(filename, 'x') as file:
            for entry in info:
                file.write(entry + '\n')

    def write_to_csv(self, filename, product):
        # If file does not exist, add header
        try:
            with open(filename, 'x') as file:
                header = "id,name,brand,categories,shades,price,size,about,ingredients,how_to_use,image_url,product_url"
                file.write(header + '\n')
        except:
            pass
        
        # Otherwise, just write product
        with open(filename, 'a') as file:
            line = ''
            line += f"{product.id},"
            line += f"\"{product.name}\","
            line += f"\"{product.brand}\","
            line += f"\"{', '.join(product.categories)}\","
            line += f"\"{', '.join(product.shades)}\","
            line += f"{product.price:.2f}," if product.price else "Not available,"
            line += f"\"{product.size}\","
            line += f"\"{product.about}\","
            line += f"\"{product.ingredients}\","
            line += f"\"{product.how_to_use}\","
            line += f"\"{product.image_url}\","
            line += f"\"{product.product_url}\""
            file.write(line + '\n')

    def scrape_brands_list(self):
        # Get response from brands list url
        brands_list_url: str = SEPHORA_URL + "brands-list"
        response = requests.get(brands_list_url, headers=USER_AGENT_HEADERS)

        # Use beautifulsoup to access html
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrape brands list and save into list
        brand_urls_list: list[str] = []
        main_box = soup.find_all('div', {'data-comp': 'BrandsList '})[0]
        for brand in main_box.find_all('li'):
            brand_urls_list.append("https://www.sephora.com" + brand.a.attrs['href'])
        
        self.brand_urls_list = brand_urls_list

    def scrape_products_list(self, brand_url: str):
        # Get response from brands url
        response = requests.get(brand_url, headers=USER_AGENT_HEADERS)

        # Use beautifulsoup to access html
        soup = BeautifulSoup(response.content, 'html.parser')

        # Scrape brands list and save into list
        product_urls_list: list[str] = []
        main_box = soup.find_all('div', {'data-comp': 'ProductGrid '})[0]
        for product in main_box.find_all('div', {'data-comp': 'ProductTile StyledComponent BaseComponent '}):
            product_link = "https://www.sephora.com" + product.a.attrs['href']
            product_link = product_link.split(' ')[0]
            product_urls_list.append(product_link)
                
        self.product_urls_list.extend(product_urls_list)

    def scrape_product_info(self, product_url):
        product = Product(product_url=product_url)

        # Set product ID
        product.id = self.product_id_counter
        self.product_id_counter += 1

        # Initialize Chrome driver (you might want to move this to __init__)
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

        has_multiple_shades: bool = False

        try:
            # Load the page
            driver.get(product_url)

            # Categories from breadcrumb
            breadcrumb = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'nav[aria-label="Breadcrumb"] ol a'))
            )
            links = driver.find_elements(By.CSS_SELECTOR, 'nav[aria-label="Breadcrumb"] ol a')
            product.categories = [link.text for link in links]
            print(product.categories)

            # Brand Name
            brand_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-at="brand_name"]'))
            )
            product.brand = brand_element.text
            print(product.brand)

            # Product name
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-at="product_name"]'))
            )
            product.name = name_element.text
            print(product.name)

            # Price
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p[data-comp="Price "] b[class^="css-"]'))
            )
            product.price = float(price_element.text.strip().replace('$', ''))
            print(product.price)

            # Size
            size_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-at="sku_name_label"]'))
            )
            product.size = size_element.text.split('-')[0].replace('Size:', '').strip()
            print(product.size)

            # Product About
            about_text = driver.execute_script("""
                const div = document.querySelector('div.css-18apj9d div, div.css-1jnhrmt div, div.css-wtwbdl div, div.css-fwckll div, div.css-1rwlp86 div, div.css-qz0qvn div');
                if (!div) return 'No match';
                
                // Create an array to hold the text content
                const contentArray = [];
                
                // Get all child nodes of the div
                const nodes = div.childNodes;
                
                // Iterate through the child nodes
                nodes.forEach(node => {
                    // Check if the node is an element node
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // If it's a <b> element, add its text and the following text
                        if (node.tagName === 'B') {
                            const title = node.textContent.trim();
                            const nextText = node.nextSibling ? node.nextSibling.textContent.trim() : '';
                            contentArray.push(title + nextText);
                        }
                    }
                });
                
                // Join the content with new lines
                return contentArray.join('\\n');
            """)
            if not about_text:
                about_text = driver.execute_script("""
                    const div = document.querySelector('div.css-18apj9d div, div.css-1jnhrmt div, div.css-wtwbdl div, div.css-fwckll div, div.css-1rwlp86 div, div.css-qz0qvn div');
                    if (!div) return '';
                    return Array.from(div.children)
                        .map(child => child.textContent.trim())
                        .join('\\n');
                """)
            product.about = about_text.replace('\n', '.').replace('"', '')
            print(product.about)

            # Product Ingredients
            ingredients_text = driver.execute_script("""
                const div = document.querySelector('#ingredients div.css-1ue8dmw div');
                if (!div) return '';
                return div.innerHTML
                    .replace(/<p>/g, '')
                    .replace(/<\\/p>/g, '\\n')
                    .replace(/<br>/g, '\\n')
                    .replace(/<[^>]*>/g, '')
                    .trim();
            """)
            product.ingredients = ingredients_text.replace('\n', '.')
            print(product.ingredients)

            # Product Use
            use_text = driver.execute_script("""
                const div = document.querySelector('div[data-at="how_to_use_section"]');
                if (!div) return '';
                return div.innerHTML
                    .replace(/<p>/g, '')
                    .replace(/<\\/p>/g, '\\n')
                    .replace(/<br>/g, '\\n')
                    .replace(/<[^>]*>/g, '')
                    .trim();
            """)
            product.how_to_use = use_text.replace('\n', '.')
            print(product.how_to_use)

            # Extract Reviews
            # product.reviews = self.scrape_product_reviews(product_url)

            # Extract Image
            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="Carousel "] button svg foreignObject img'))
            )
            product.image_url = image_element.get_attribute('src')  # Get the image URL
            print(product.image_url)

            # Extract Shades if Multiple Shades
            product.shades = self.scrape_product_shade_names(product_url)
            print(product.shades)

            self.product_database.append(product)
            self.write_to_csv('products.csv', product)
            
        finally:
            driver.quit()

    def scrape_product_shade_names(self, product_url):
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
        
        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)
        shade_names = []
        
        try:
            driver.get(product_url)  # Navigate to the product page
            swatch_group = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="SwatchGroup "]'))
            )
            shade_buttons = WebDriverWait(swatch_group, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-at="selected_swatch"], button[data-at="swatch"]'))
            )
            for button in shade_buttons:
                button_name = button.get_attribute('aria-label')  # Get the button name
                button_name = button_name.replace(' - Selected', '')
                shade_names.append(button_name)
        
        finally:
            driver.quit()

        return shade_names
        
    
    def scrape_product_shades(self, product_url):
        # Initialize Chrome driver (you might want to move this to __init__)
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
        
        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

        try:
            driver.get(product_url)  # Navigate to the product page

            # Initialize shades list
            shades: list[Shade] = []

            # Find only the first swatch group
            swatch_group = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="SwatchGroup "]'))
            )

            # Within the first swatch group, find all shade buttons
            shade_buttons = WebDriverWait(swatch_group, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[data-at="selected_swatch"], button[data-at="swatch"]'))
            )

            # Parse through all shade buttons to extract name and image url
            for button in shade_buttons:
                button_name = button.get_attribute('aria-label')  # Get the button name

                # Use Selenium to find the first button with the aria-label equal to button_name
                new_button = driver.find_element(By.CSS_SELECTOR, f'button[aria-label="{button_name}"]')

                # Use JavaScript to click the button
                driver.execute_script("arguments[0].click();", new_button)
                time.sleep(2)

                # Extract Shade Name
                shade_label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="SwatchDescription "] span'))
                )
                shade_info = shade_label.text
                shade_info = shade_info.split(': ')[-1]
                shade_name, shade_description = shade_info.rsplit(' - ',1)

                # Extract Image
                image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="Carousel "] button svg foreignObject img'))
                )

                # Get the image URL from the first instance found
                image_url = image_element.get_attribute('src')  # Get the image URL
                
                # Create shade object and add to list
                curr_shade = Shade(name=shade_name, descriptor=shade_description, image_url=image_url)
                shades.append(curr_shade)
                # print(curr_shade)
        
        finally:
            driver.quit()

        return shades
    
    def scrape_product_reviews(self, product_url):
        reviews: list[Review] = []
        return reviews