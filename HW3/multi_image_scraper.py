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
from tqdm import tqdm

def get_product_images(json_file_path, save_folder):
    """
    Uses Selenium to load a product page, scrapes up to three gallery
    images using the thumbnail selector, and saves them.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Prevents the "DevTools listening on..." message
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Selenium WebDriver initialized.")
    except Exception as e:
        print(f"❌ Failed to initialize WebDriver: {e}")
        return

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"Created directory: {save_folder}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        # Sort products by product_id to process them in a predictable order
        products.sort(key=lambda p: int(p.get('product_id', 0)))
    except Exception as e:
        print(f"❌ Error reading or sorting JSON file: {e}")
        driver.quit()
        return

    for product in tqdm(products, desc="Scraping Product Images"):
        try:
            product_id = product.get('product_id')
            if not product_id:
                tqdm.write("Skipping entry missing 'product_id'.")
                continue

            # Checks for files like "product_id_0.jpg" to see if we've processed it.
            search_pattern = os.path.join(save_folder, f"{product_id}_*")
            if glob.glob(search_pattern):
                tqdm.write(f"🖼️ Images for product ID {product_id} already exist. Skipping.")
                continue

            url = f"https://www.digikala.com/product/dkp-{product_id}/"
            
            tqdm.write(f"Processing product ID: {product_id}")

            driver.get(url)
            
            time.sleep(4) 
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # This now targets the img tag inside the specific thumbnail divs.
            image_tags = soup.select('div[data-cro-id="pdp-album-open"] img')
            
            if image_tags:
                tqdm.write(f"  Found {len(image_tags)} thumbnail images for {product_id}. Downloading up to 3...")
                
                # Loop through the first 3 images found.
                for index, image_tag in enumerate(image_tags[:3]):
                    if image_tag.get('src'):
                        image_url = image_tag['src'].split('?')[0] # Clean URL
                        tqdm.write(f"    Downloading image {index + 1} from: {image_url}")

                        try:
                            image_response = requests.get(image_url, timeout=10)
                            image_response.raise_for_status()

                            file_extension = os.path.splitext(image_url)[-1] or '.jpg'
                            
                            # Append an index to each filename (e.g., "12345_0.jpg")
                            image_path = os.path.join(save_folder, f"{product_id}_{index}{file_extension}")
                            
                            with open(image_path, 'wb') as f:
                                f.write(image_response.content)
                            tqdm.write(f"    ✅ Successfully saved image to {image_path}")

                        except requests.exceptions.RequestException as req_err:
                             tqdm.write(f"    ❌ Failed to download image {index + 1}: {req_err}")

            else:
                tqdm.write(f"  ❌ Could not find any thumbnail images for product ID: {product_id}")

        except Exception as e:
            tqdm.write(f"  ❌ An unexpected error occurred for product ID {product_id}: {e}")

    driver.quit()
    print("👍 WebDriver closed. Process complete.")


json_path = 'products.json'
output_folder = 'product_images'

get_product_images(json_path, output_folder)
