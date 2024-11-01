from product_info import Product, Shade, Review
from sephora_scraper import SephoraScraper

def generate_products():
    scraper = SephoraScraper(product_database=[])
    scraper.scrape_brands_list()
    for brand_url in scraper.brand_urls_list:
        scraper.scrape_products_list(brand_url)
        break

if __name__ == "__main__": 
    generate_products()