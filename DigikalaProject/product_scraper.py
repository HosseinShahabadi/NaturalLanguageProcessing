import requests
import csv
import time
import math
import os

# --- Configuration ---
PRODUCTS_PER_PAGE = 20
TARGET_PRODUCT_COUNT = 16000
START_PAGE = 550 # Default 1
PAGES_TO_SCRAPE = math.ceil(TARGET_PRODUCT_COUNT / PRODUCTS_PER_PAGE)

# Output file name
OUTPUT_FILE = "digikala_products.csv"
IMAGE_URLS_DIR = "image_urls"  # Folder for image CSV files

def get_product_list(page):
    """Fetches a list of products from the generic search/listing page."""
    url = f"https://api.digikala.com/v1/search/?page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('products', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product list on page {page}: {e}")
        return []


def get_product_details(product_id):
    """Fetches detailed product information from the v2 product API."""
    url = f"https://api.digikala.com/v2/product/{product_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}).get('product', {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for product {product_id}: {e}")
        return {}


def get_product_images(product_data):
    """Extracts all available image URLs from product details (works for both search and detail APIs)."""
    image_urls = []
    
    images_data = product_data.get('images', {})
    if not images_data:
        return image_urls

    # Get all main images
    main_images = images_data.get('main', {}).get('url', [])
    if main_images and isinstance(main_images, list):
        for url in main_images:
            if url:  # Ensure the URL is not empty or None
                image_urls.append(url)

    # Get all images from the list
    other_images = images_data.get('list', [])
    for image in other_images:
        img_urls = image.get('url', [])
        if img_urls and isinstance(img_urls, list):
            for url in img_urls:
                if url:  # Ensure the URL is not empty or None
                    image_urls.append(url)

    return image_urls


def extract_description(product_data):
    """Extracts the description from the review section and cleans it."""
    try:
        description = product_data.get('review', {}).get('description', 'N/A')
        if description and description != 'N/A':
            # Replace newlines and other special characters with a space
            description = description.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            # Remove extra spaces
            description = ' '.join(description.split())
        return description.strip() if description else 'N/A'
    except:
        return 'NULL'


def extract_comments_overview(product_data):
    """Extracts the overview from the comments_overview section and cleans it."""
    try:
        overview = product_data.get('comments_overview', {}).get('overview', 'NULL')
        if overview and overview != 'NULL':
            # Replace newlines and other special characters with a space
            overview = overview.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            # Remove extra spaces
            overview = ' '.join(overview.split())
        return overview.strip() if overview and overview != 'NULL' else 'NULL'
    except:
        return 'NULL'


def save_images_to_csv(product_id, image_urls):
    """Saves all image URLs to a separate CSV file named after product_id in the image_urls folder."""
    if not image_urls or all(url == 'N/A' for url in image_urls):
        return
    if not os.path.exists(IMAGE_URLS_DIR):
        os.makedirs(IMAGE_URLS_DIR)
    image_file = os.path.join(IMAGE_URLS_DIR, f"{product_id}_images.csv")
    with open(image_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        for url in image_urls:
            writer.writerow([url])


def main():
    """Main function to orchestrate the scraping process."""
    all_products_data = []
    print("=== Starting scrape for general products from digikala.com/search/ ===")
    print(f"Aiming for ~{TARGET_PRODUCT_COUNT} products across {PAGES_TO_SCRAPE} pages.")

    current_product = 0
    for page_num in range(START_PAGE, PAGES_TO_SCRAPE + 1):
        if len(all_products_data) >= TARGET_PRODUCT_COUNT:
            print(f"Target of {TARGET_PRODUCT_COUNT} products reached. Stopping.")
            break

        print(f"\nScraping general product page {page_num} of {PAGES_TO_SCRAPE}...")
        products = get_product_list(page_num)

        if not products:
            print("No more products found. Stopping.")
            break

        for product in products:
            if len(all_products_data) >= TARGET_PRODUCT_COUNT:
                break

            current_product += 1
            product_id = product.get('id')
            if not product_id:
                continue

            # Basic info from search (fallback)
            title_en = product.get('title_en', 'N/A')
            title_fa = product.get('title_fa', 'N/A')
            rate = product.get('rating', {}).get('rate', 0)
            rate_count = product.get('rating', {}).get('count', 0)

            print(f"  -> Fetching details for ID {product_id} (Product {current_product}/{TARGET_PRODUCT_COUNT}): {title_fa[:30]}...")
            
            # Fetch detailed product data
            product_detail = get_product_details(product_id)
            
            # Override with detail data if available
            if product_detail:
                title_en = product_detail.get('title_en', title_en)
                title_fa = product_detail.get('title_fa', title_fa)
                rate = product_detail.get('rating', {}).get('rate', rate)
                rate_count = product_detail.get('rating', {}).get('count', rate_count)
                image_list = get_product_images(product_detail)
                description = extract_description(product_detail)
                comments_overview = extract_comments_overview(product_detail)
                # print(f"    Review Description preview: {description[:100]}...")
                # print(f"    Comments Overview preview: {comments_overview[:100]}...")
                print(f"    Found {len(image_list)} image URLs.")
            else:
                # Fallback to search data
                image_list = get_product_images(product)
                description = 'N/A'
                comments_overview = 'NULL'
                # print(f"    Warning: No details fetched, using fallback. Description: {description[:50]}...")

            all_products_data.append({
                'id': product_id,
                'title_en': title_en,
                'title_fa': title_fa,
                'Rate': rate,
                'Rate_cnt': rate_count,
                'introduction': description,
                'comments_overview': comments_overview
            })
            
            # Save all images to a separate CSV in the image_urls folder
            save_images_to_csv(product_id, image_list)
            
            time.sleep(0.2)  # Polite delay

    # --- Save data to CSV ---
    if all_products_data:
        print(f"\n✅ Scrape complete! Writing {len(all_products_data)} products to {OUTPUT_FILE}...")
        if os.path.exists(OUTPUT_FILE):
            # File exists, append without writing header
            with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'title_en', 'title_fa', 'Rate', 'Rate_cnt', 'introduction', 'comments_overview'])
                writer.writerows(all_products_data)
        else:
            # File doesn't exist, write with header
            with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8-sig') as file:
                fieldnames = ['id', 'title_en', 'title_fa', 'Rate', 'Rate_cnt', 'introduction', 'comments_overview']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_products_data)
        print("🎉 Done!")
    else:
        print("No data was scraped.")


if __name__ == "__main__":
    main()
