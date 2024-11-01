import requests
from bs4 import BeautifulSoup

SEPHORA_URL: str = "https://www.sephora.com/ca/en/"

def scrape_brands_list():
    # Get response from brands list url
    brands_list_url: str = SEPHORA_URL + "brands-list"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    response = requests.get(brands_list_url, headers=headers)

    # Use beautifulsoup to access html
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape brands list and save into list
    brand_urls_list: list[str] = []
    main_box = soup.find_all('div', {'data-comp': 'BrandsList '})[0]
    for brand in main_box.find_all('li'):
        brand_urls_list.append("https://www.sephora.com" + brand.a.attrs['href'])
    
    return brand_urls_list

if __name__ == "__main__": 
    brands_urls_list: list[str] = scrape_brands_list()
