import json
import requests
from bs4 import BeautifulSoup
import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_product_images(json_file_path, save_folder):
    """
    Checks if an image exists first. If not, uses Selenium to load the page,
    scrapes the main image, and saves it.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Selenium WebDriver initialized.")
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"Created directory: {save_folder}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        driver.quit()
        return

    for product in products:
        try:
            product_id = product.get('product_id')
            if not product_id:
                print("Skipping entry missing a 'product_id'.")
                continue

            search_pattern = os.path.join(save_folder, f"{product_id}.*")
            
            if glob.glob(search_pattern):
                print(f"Image for product ID {product_id} already exists. Skipping.")
                continue

            url = f"https://www.digikala.com/product/dkp-{product_id}/"
            print(f"Processing product ID: {product_id} at {url}")

            driver.get(url)
            time.sleep(3) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            possible_selectors = [
                'img.w-full.rounded-large.overflow-hidden.inline-block',
                'img.w-full.object-contain'
            ]

            image_tag = None
            for selector in possible_selectors:
                image_tag = soup.select_one(selector)
                if image_tag:
                    break

            if image_tag and image_tag.get('src'):
                image_url = image_tag['src']
                print(f"  Downloading image from: {image_url}")

                image_response = requests.get(image_url)
                image_response.raise_for_status()

                file_extension = os.path.splitext(image_url.split('?')[0])[-1] or '.jpg'
                image_path = os.path.join(save_folder, f"{product_id}{file_extension}")
                
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"  Successfully saved image to {image_path}\n")
            else:
                print(f"  Could not find the main image for product ID: {product_id}\n")

        except Exception as e:
            print(f"  An unexpected error occurred for product ID {product_id}: {e}\n")

    driver.quit()
    print("WebDriver closed.")


json_path = 'products.json'
output_folder = 'product_images'

get_product_images(json_path, output_folder)
