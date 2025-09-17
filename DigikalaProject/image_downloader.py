import csv
import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm
import time

# --- Configuration ---
IMAGE_URLS_DIR = "image_urls"  # Folder containing image URL CSV files
IMAGES_DIR = "images"          # Folder to save downloaded images
K = 3                          # Number of images to download per product

def download_image(url, save_path):
    """Downloads an image from the given URL and saves it to the specified path."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        # print(f"Downloaded {save_path}")
    except requests.exceptions.RequestException as e:
        # print(f"Failed to download {url}: {e}")
        return

def process_image_csvs():
    """Reads each CSV in image_urls folder, downloads up to K images per product, skipping if already exists."""
    if not os.path.exists(IMAGE_URLS_DIR):
        print(f"Error: {IMAGE_URLS_DIR} folder not found.")
        return

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    # Get all CSV files in image_urls folder
    csv_files = [f for f in os.listdir(IMAGE_URLS_DIR) if f.endswith('_images.csv')]
    if not csv_files:
        print(f"No CSV files found in {IMAGE_URLS_DIR}.")
        return

    for csv_file in tqdm(csv_files, desc="Processing CSV files", total=len(csv_files)):
        product_id = csv_file.replace('_images.csv', '')
        # print(f"Processing images for product ID {product_id}...")
        
        csv_path = os.path.join(IMAGE_URLS_DIR, csv_file)
        image_urls = []
        
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Ensure row is not empty
                    image_urls.append(row[0])  # Assuming each row has one URL
        
        # Download up to K images, skipping if file exists
        for i in range(min(K+1, len(image_urls))):
            if i == 0:
                filename = f"{product_id}.jpg"
            elif i == 1:
                continue
            else:
                filename = f"{product_id}_{i-1}.jpg"
            save_path = os.path.join(IMAGES_DIR, filename)
            
            if os.path.exists(save_path):
                # print(f"Skipping {save_path} (already exists)")
                continue
            
            download_image(image_urls[i], save_path)
        
        time.sleep(0.1)  # Polite delay

if __name__ == "__main__":
    process_image_csvs()
