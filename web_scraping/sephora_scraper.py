import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
from pydantic import BaseModel # type: ignore
from product_info import Product, Shade, Review

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
    
    def write_to_file(self, filename, info):
        with open(filename, 'x') as file:
            for entry in info:
                file.write(entry + '\n')