from product_info import Product, Shade, Review
from sephora_scraper import SephoraScraper

def generate_products():
    scraper = SephoraScraper(product_database=[])
    scraper.scrape_brands_list()
    for brand_url in scraper.brand_urls_list:
        scraper.scrape_products_list(brand_url)

    scraper.write_to_file('brands.txt', scraper.brand_urls_list)
    scraper.write_to_file('products.txt', scraper.product_urls_list)

def test_product():
    scraper = SephoraScraper(product_database=[])
    scraper.scrape_product_info('https://www.sephora.com/ca/en/product/aavrani-hair-density-boosting-treatment-P510710?skuId=2760346&icid2=products%20grid:p510710:product')

if __name__ == "__main__": 
    test_product()