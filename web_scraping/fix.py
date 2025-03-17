import os
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
import json
import re

def find_info(product_url):
    # Initialize Chrome driver (you might want to move this to __init__)
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
    driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

    try:
        # Load the page
        driver.get(product_url)
        
        overall_rating = -1
        num_reviews = 0
        image_url = ''

        try:
            # Get image url
            image_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-comp="Carousel "] button svg foreignObject img'))
            )
            image_url = image_element.get_attribute('src')  # Get the image URL
            print(image_url)
        except:
            pass
        
        try:
            # Wait for the ratings-reviews-container to be present
            reviews_container = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#ratings-reviews-container'))
            )

            # Scroll to the reviews container
            driver.execute_script("arguments[0].scrollIntoView();", reviews_container)

            time.sleep(5)

            # Get overall rating
            rating = reviews_container.find_element(By.CSS_SELECTOR, '[class="css-1ac1x0l eanm77i0"]')
            overall_rating = float(rating.text)
            print(overall_rating)
            
            # Get num reviews
            review_count = reviews_container.find_element(By.CSS_SELECTOR, '[class="css-nv7myq eanm77i0"]')
            print(review_count.text)
            num_reviews = int((review_count.text).replace(',','').split(' ')[0])
            print(num_reviews)

        except:
            pass

        
    finally:
        driver.quit()
    
    return float(overall_rating), int(num_reviews), image_url


def add_num_reviews_rating():
    products_dir = '/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products'
    
    for count in range(1152,1797):
        filename = "product_id_" + str(count) + ".json"
        filename = os.path.join(products_dir, filename)
        if not os.path.isfile(filename):
            continue

        print(filename)
        fix_product = False
        
        with open(filename, 'r') as file:
            content = file.read()

            # Get product url
            product_url = ''
            for line in content.splitlines():
                if '"num_reviews": 0' in line:
                    fix_product = True
                if "product_url" in line:
                    elements = line.split('"')
                    for element in elements:
                        if 'sephora' in element:
                            product_url = element
        
        if not fix_product:
            continue

        overall_rating, num_reviews, image_url = find_info(product_url)
        
        with open(filename, 'w') as file:
            count = 1
            for line in content.splitlines():
                if '"size":' in line:
                    continue
                if '"num_reviews": 0' in line:
                    file.write(f'\n\t"num_reviews": {num_reviews},')
                    count += 1
                    continue
                if count == 10 and 'num_reviews' not in line:
                    file.write(f'\n\t"num_reviews": {num_reviews},')
                    count += 1
                
                if '"overall_rating": -1.0,' in line and overall_rating != -1:
                    file.write(f'\n\t"overall_rating": {overall_rating},')
                    count += 1
                    continue
                if count == 11 and 'overall_rating' not in line:
                    file.write(f'\n\t"overall_rating": {overall_rating},')
                    count += 1

                if count == 13 and 'image_url' not in line:
                    file.write(f'\n\t"image_url": "{image_url}",')
                    count += 1
                
                if count != 1:
                    file.write('\n')

                file.write(line)
                count += 1

def clean_invalid_quotes(input_file, output_file):
    try:
        with open(input_file, 'r') as file:
            content = file.read()

        # New section to eliminate misplaced quotation marks
        # Remove any quotation marks that are not properly placed
        cleaned_content = re.sub(r'(?<!\t)(?<!:\s)"(?!(,\n)|:|\n)', '', content)
        cleaned_content = re.sub(r'\\(?![ntbrfv])', '', content)

        # Validate and save the cleaned JSON
        try:
            json_data = json.loads(cleaned_content)  # Check if the cleaned JSON is valid
            with open(output_file, 'w') as file:
                json.dump(json_data, file, indent=4)
            print(f"Cleaned JSON saved to {output_file}")
        except json.JSONDecodeError as e:
            print("Error: The JSON is still invalid after cleaning.", e)

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__": 
    for count in range(1, 1797):
        filename = "/Users/floriafang/Documents/UofT/capstone/Personal-Shopping-Site/web_scraping/products/product_id_" + str(count) + ".json"
        print(filename)
        clean_invalid_quotes(filename, filename)