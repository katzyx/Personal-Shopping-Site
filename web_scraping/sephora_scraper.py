import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from pydantic import BaseModel # type: ignore
from product_info import Product, Shade, Review
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore

SEPHORA_URL: str = "https://www.sephora.com/ca/en/"
USER_AGENT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

class SephoraScraper(BaseModel):
    product_database: list[Product] # Database of all products
    brand_urls_list: list[str] = [] # List of brand urls
    product_urls_list: list[str] = [] # List of product urls

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
        product = Product()

        # Initialize Chrome driver (you might want to move this to __init__)
        driver = webdriver.Chrome()

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

            # Brand Name
            brand_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-at="brand_name"]'))
            )
            product.brand = brand_element.text

            # Product name
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-at="product_name"]'))
            )
            product.name = name_element.text

            # Price
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'p[data-comp="Price "] b.css-0'))
            )
            product.price = float(price_element.text.strip().replace('$', ''))

            # Size
            size_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-at="sku_name_label"]'))
            )
            if 'Size' not in size_element.text:
                size_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-at="sku_size_label"]'))
                )
                has_multiple_shades = True
            product.size = size_element.text.split('-')[0].replace('Size:', '').strip()

            # Extract Shades if Multiple Shades

            # Product About
            about_text = driver.execute_script("""
                const div = document.querySelector('div.css-18apj9d div, div.css-1jnhrmt div');
                if (!div) return '';
                return Array.from(div.children)
                    .map(child => child.textContent.trim())
                    .join('\\n');
            """)
            product.about = about_text

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
            product.ingredients = ingredients_text

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
            product.how_to_use = use_text

            # Extract Reviews

            print(product)

            self.product_database.append(product)
            
        finally:
            driver.quit()

    
    def write_to_file(self, filename, info):
        with open(filename, 'x') as file:
            for entry in info:
                file.write(entry + '\n')