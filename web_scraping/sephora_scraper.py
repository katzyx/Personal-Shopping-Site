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

    def write_to_file(self, product: Product):
        filename = "product_id_" + str(product.id) + ".json"
        
        # Clean and escape special characters
        product.ingredients = product.ingredients.replace('&nbsp;', ' ').replace('<', '').replace('>', '')
        product.about = product.about.replace('&nbsp;', ' ').replace('<', '').replace('>', '')
        product.how_to_use = product.how_to_use.replace('&nbsp;', ' ').replace('<', '').replace('>', '')

        with open(filename, 'x') as file:
            file.write('{')

            # Write product attributes
            file.write(f'\n\t"product_id": "{product.id}",')
            file.write(f'\n\t"name": "{product.name}",')
            file.write(f'\n\t"brand": "{product.brand}",')
            categories_string = ', '.join(f'{category}' for category in product.categories)
            file.write(f'\n\t"categories": "{categories_string}",')
            file.write(f'\n\t"price": {product.price},')
            # file.write(f'\n\t"size": "{product.size}",')
            file.write(f'\n\t"about": "{product.about}",')
            file.write(f'\n\t"ingredients": "{product.ingredients}",')
            file.write(f'\n\t"how_to_use": "{product.how_to_use}",')
            file.write(f'\n\t"num_reviews": {product.num_reviews},')
            file.write(f'\n\t"overall_rating": {product.overall_rating},')
            file.write(f'\n\t"product_url": "{product.product_url}",')
            file.write(f'\n\t"image_url": "{product.image_url}",')

            # Write product shades
            file.write(f'\n\t"shades": [')
            for index, shade in enumerate(product.shades):
                file.write(f'\n\t\t{{')
                file.write(f'\n\t\t\t"shade_name": "{shade.name}",')
                file.write(f'\n\t\t\t"shade_descriptor": "{shade.descriptor}",')
                file.write(f'\n\t\t\t"shade_image_url": "{shade.image_url}"')
                file.write(f'\n\t\t}}')
                
                if index < len(product.shades) - 1:
                    file.write(f',')
            file.write(f'\n\t],')

            # Write product reviews
            file.write(f'\n\t"reviews": [')
            for index, review in enumerate(product.reviews):
                file.write(f'\n\t\t{{')
                file.write(f'\n\t\t\t"review_title": "{review.title}",')
                file.write(f'\n\t\t\t"review_rating": {review.rating},')
                file.write(f'\n\t\t\t"review_shade_purchased": "{review.shade_purchased}",')
                file.write(f'\n\t\t\t"review_buyer_description": "{review.buyer_description}",')
                file.write(f'\n\t\t\t"review_text": "{review.review}"')
                file.write(f'\n\t\t}}')
                
                if index < len(product.reviews) - 1:
                    file.write(f',')
            file.write(f'\n\t]')

            file.write('\n}')

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
        print(product.id)
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
            try:
                size_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-at="sku_name_label"]'))
                )
                product.size = size_element.text.split('-')[0].replace('Size:', '').strip()
                print(product.size)
            except:
                product.size = ''

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
            try:
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
            except:
                product.how_to_use = ''

            # Extract Image
            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="Carousel "] button svg foreignObject img'))
            )
            product.image_url = image_element.get_attribute('src')  # Get the image URL
            print(product.image_url)

            # Extract Review Info
            try:
                # Wait for the ratings-reviews-container to be present
                reviews_container = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#ratings-reviews-container'))
                )

                # Scroll to the reviews container
                driver.execute_script("arguments[0].scrollIntoView();", reviews_container)

                time.sleep(2)

                # Get overall rating
                rating = reviews_container.find_element(By.CSS_SELECTOR, '[class="css-1ac1x0l eanm77i0"]')
                product.overall_rating = float(rating.text)
                print(product.overall_rating)
                
                # Get num reviews
                review_count = reviews_container.find_element(By.CSS_SELECTOR, '[class="css-nv7myq eanm77i0"]')
                product.num_reviews = int((review_count.text).replace(',', '').split(' ')[0])
                print(product.num_reviews)

            except:
                product.overall_rating = -1
                product.num_reviews = 0

            # Extract Shades if Multiple Shades
            product.shades = self.scrape_product_shades(product_url)

            # Extract Reviews
            product.reviews = self.scrape_product_reviews(product_url)

            self.product_database.append(product)
            self.write_to_file(product)
            
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

        # Initialize shades list
        shades: list[Shade] = []
        
        try:
            driver.get(product_url)  # Navigate to the product page

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
                # Check for popup again before each interaction
                try:
                    popup_close_button = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-at="modal_close"]'))
                    )
                    popup_close_button.click()
                except TimeoutException:
                    pass

                button_name = button.get_attribute('aria-label')
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
                if len(shade_info.rsplit(' - ',1)) > 1:
                    shade_name, shade_description = shade_info.rsplit(' - ',1)
                else: 
                    shade_name = shade_info
                    shade_description = ''

                # Extract Image
                image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="Carousel "] button svg foreignObject img'))
                )

                # Get the image URL from the first instance found
                image_url = image_element.get_attribute('src')  # Get the image URL
                
                # Create shade object and add to list
                curr_shade = Shade(name=shade_name, descriptor=shade_description, image_url=image_url)
                shades.append(curr_shade)
                print(curr_shade)
        
        except:
            pass
        
        finally:
            driver.quit()

        return shades
    
    def scrape_product_reviews(self, product_url):
        # Initialize Chrome driver (you might want to move this to __init__)
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

        # Initialize shades list
        reviews: list[Review] = []
        
        try:
            driver.get(product_url)  # Navigate to the product page

            while True:
                try:
                    popup_close_button = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-at="modal_close"]'))
                    )
                    popup_close_button.click()
                except TimeoutException:
                    pass

                # Wait for the ratings-reviews-container to be present
                reviews_container = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#ratings-reviews-container'))
                )

                # Scroll to the reviews container
                driver.execute_script("arguments[0].scrollIntoView();", reviews_container)

                # Wait for a moment to ensure that the reviews have time to load
                time.sleep(2)

                
                # Now find all review containers within the reviews_container
                review_elements = reviews_container.find_elements(By.CSS_SELECTOR, 'div[data-comp="Review StyledComponent BaseComponent "]')
                
                # Iterate through each review container and extract data
                for review in review_elements:
                    # Initialize variables
                    review_title = ''
                    review_rating = ''
                    review_shade = ''
                    review_buyer = ''
                    review_text = ''

                    # Check for popup again before each interaction
                    try:
                        popup_close_button = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-at="modal_close"]'))
                        )
                        popup_close_button.click()
                    except TimeoutException:
                        pass

                    # Extract star rating
                    try:
                        star_rating = review.find_element(By.CSS_SELECTOR, '[data-comp="StarRating "]')
                        review_rating = star_rating.get_attribute('aria-label')
                        review_rating = int(review_rating.strip().replace('stars', '').replace('star', ''))
                        # print(review_rating)
                    except:
                        pass

                    # Extract review title
                    try:
                        title = review.find_element(By.CSS_SELECTOR, '[class="css-m9drnf eanm77i0"]')
                        review_title = title.text
                        review_title = review_title.replace('\n', ' ').replace('"','')
                        # print(review_title)
                    except:
                        pass

                    # Extract shade purchased
                    try:
                        shade_container = review.find_element(By.CSS_SELECTOR, '[class="css-ae7pay eanm77i0"]')
                        shade_element = shade_container.find_element(By.TAG_NAME, 'span')
                        review_shade = shade_element.text
                        # print(review_shade)
                    except:
                        pass

                    # Extract buyer description
                    try:
                        description_element = WebDriverWait(review, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[class="css-2h4ti5 eanm77i0"]'))
                        )
                        if description_element:
                            review_buyer = description_element.text
                            # print(review_buyer)
                    except:
                        pass

                    # Extract review
                    try:
                        # Extract review
                        product_review = WebDriverWait(review, 1).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[class="css-1pw69zl eanm77i0"]'))
                        )
                        review_text = product_review.text
                        review_text = review_text.replace('\n', ' ').replace('"','')
                        # print(review_text)
                    except:
                        pass

                    curr_review = Review(
                        title=review_title,
                        rating=review_rating,
                        shade_purchased=review_shade,
                        buyer_description=review_buyer,
                        review=review_text
                    )
                    reviews.append(curr_review)
                
                # Find next page button and click if enabled
                try:
                    nextPageButton = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Next page"]'))
                    )
                    
                    # Scroll the button into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", nextPageButton)
                    time.sleep(1)  # Give time for any animations to complete
                    
                    # Check if button is enabled
                    if nextPageButton and not nextPageButton.get_attribute('disabled'):
                        # Try to remove any overlapping elements
                        driver.execute_script("""
                            var elements = document.querySelectorAll('[data-at="shop_btn"]');
                            elements.forEach(function(element) {
                                element.style.display = 'none';
                            });
                        """)
                        
                        # Click using JavaScript instead of direct click
                        driver.execute_script("arguments[0].click();", nextPageButton)
                    else:
                        break
                    
                except:
                    break
                
            print(reviews)

        except:
            pass
        
        finally:
            driver.quit()

        return reviews