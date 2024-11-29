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
    scraper.scrape_product_info('https://www.sephora.com/ca/en/product/genius-liquid-collagen-P421277?skuId=2610616&icid2=products')
    # print(scraper.product_database[0])
    
    # shades: list[Shade] = scraper.scrape_product_shades('https://www.sephora.com/ca/en/product/hollywood-flawless-filter-P434104?skuId=2116010')
    # for shade in shades:
    #     print(shade)

def test_all_products():
    scraper = SephoraScraper(product_database=[])
    with open('products.txt', 'r') as file:
        for line in file:
            try:
                scraper.scrape_product_info(line.strip())
            except:
                pass

if __name__ == "__main__": 
    test_all_products()