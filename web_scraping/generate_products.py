from product_info import Product, Shade, Review
from sephora_scraper import SephoraScraper

def generate_products():
    scraper = SephoraScraper(product_database=[])
    scraper.scrape_brands_list()
    for brand_url in scraper.brand_urls_list:
        scraper.scrape_products_list(brand_url)

    scraper.write_to_file('brands.txt', scraper.brand_urls_list)
    scraper.write_to_file('web_scraping/products.txt', scraper.product_urls_list)

def test_product():
    scraper = SephoraScraper(product_database=[])
    scraper.scrape_product_info('https://www.sephora.com/ca/en/product/valentino-very-valentino-24-hour-long-wear-liquid-foundation-P501593?skuId=2615631&icid2=products%20grid:p501593:product')
    
    # shades: list[Shade] = scraper.scrape_product_shades('https://www.sephora.com/ca/en/product/valentino-very-valentino-24-hour-long-wear-liquid-foundation-P501593?skuId=2615631&icid2=products%20grid:p501593:product')

    # reviews: list[Review] = scraper.scrape_product_reviews('https://www.sephora.com/ca/en/product/valentino-very-valentino-24-hour-long-wear-liquid-foundation-P501593?skuId=2615631&icid2=products%20grid:p501593:product')

def test_all_products():
    scraper = SephoraScraper(product_database=[])
    with open('web_scraping/products.txt', 'r') as file:
        for line in file:
            try:
                scraper.scrape_product_info(line.strip())
            except:
                pass

def test_write():
    scraper = SephoraScraper(product_database=[])

    # Initialize an empty Shade and Review
    empty_shade = Shade(name='', descriptor='', image_url='')
    empty_review = Review(title='', rating=0, shade_purchased='', buyer_description='', review='')

    # Initialize a Product with all empty attributes and include the empty Shade and Review
    empty_product = Product(
        id=0,
        name='',
        brand='',
        categories=['Makeup', 'Face'],
        shades=[empty_shade, empty_shade],  # List containing one empty Shade object
        price=0,
        size='',
        about='',
        ingredients='',
        how_to_use='',
        reviews=[empty_review],  # List containing one empty Review object
        image_url='',
        product_url=''
    )

    scraper.write_to_file(empty_product)

if __name__ == "__main__": 
    test_product()
