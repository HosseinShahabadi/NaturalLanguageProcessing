import pandas as pd
import openai
import os
import time
from API import ApiClient
from tqdm import tqdm

# --- Configuration ---

# 1. SET YOUR API KEY
# It's best practice to set this as an environment variable to keep it secure.
# For example, in your terminal: export OPENAI_API_KEY='your_key_here'
# If you can't set an environment variable, you can uncomment the next line and paste your key.
# openai.api_key = "YOUR_API_KEY_HERE"

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✅ API Key found successfully.")
else:
    print("❌ ERROR: The 'OPENAI_API_KEY' environment variable was not found.")
    print("Please make sure it is set correctly before running the script.")

# 2. FILE AND MODEL SETTINGS
INPUT_FILE = './longest_comments_for_top_rated_products.csv'
OUTPUT_FILE = 'product_summaries.csv'

# --- Prompt Template ---
# This is the instruction we will send to the model for each product.
PROMPT_TEMPLATE = """
Based *only* on the following user comments for a single product, please provide a concise summary in Persian.
Do not invent any features or points not mentioned in the comments.
Please be objective and reflect the overall sentiment of the provided text.
Your answer must be smaller than 450 tokens.

Here are the comments:
---
{comments_text}
---

Summary in Persian:
"""


def get_summary_from_api(product_comments, retries=3, delay=5):
    """
    Calls the OpenAI API to get a summary for a block of comments.
    Includes basic retry logic for handling transient API errors.
    """
    global number_of_api_calls
    prompt = PROMPT_TEMPLATE.format(comments_text=product_comments)
    for attempt in range(retries):
        try:
            number_of_api_calls += 1
            return Client._request(prompt)
        except Exception as e:
            print(f"API call failed on attempt {attempt + 1}/{retries}. Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this product.")
                return f"Error: API call failed after {retries} retries."


def generate_summaries():
    """
    Main function to orchestrate the summary generation process.
    """
    print("--- Starting Product Summary Generation ---")
    
    # Load the filtered comments
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found. Please run the previous script first.")
        return

    # --- Resume Logic ---
    # Check if an output file already exists to avoid re-processing.
    if os.path.exists(OUTPUT_FILE):
        print(f"Found existing output file: '{OUTPUT_FILE}'. Resuming from where we left off.")
        summaries_df = pd.read_csv(OUTPUT_FILE)
        processed_ids = summaries_df['product_id'].unique().tolist()
        results = summaries_df.to_dict('records')
    else:
        processed_ids = []
        results = []

    # Group comments by product
    product_groups = df.groupby('product_id')

    # Filter out already processed products
    products_to_process = {pid: group for pid, group in product_groups if pid not in processed_ids}

    if not products_to_process:
        print("All products have already been summarized. Process complete.")
        return

    # --- Main Loop ---
    print(f"Found {len(products_to_process)} new products to summarize.")
    for product_id, group in tqdm(products_to_process.items(), desc="Summarizing Products"):
        # Combine all comment bodies into a single text block
        all_comments_text = "\n\n---\n\n".join(group['body'].dropna().astype(str))

        # Call the API to get the summary
        summary = get_summary_from_api(all_comments_text)
        
        # Append the new result
        results.append({'product_id': product_id, 'summary': summary})

        # --- Save Progress ---
        # We save after each API call to ensure no work is lost.
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

    print("\n--- Process Complete! ---")
    print(f"All summaries have been saved to '{OUTPUT_FILE}'.")


if __name__ == '__main__':
    # Before running, ensure you have the required libraries installed:
    # pip install pandas openai tqdm
    
    if not api_key:
        print("FATAL ERROR: OpenAI API key is not configured.")
        print("Please set the OPENAI_API_KEY environment variable or set it in the script.")
    else:
        Client = ApiClient()
        number_of_api_calls = 0
        generate_summaries()

        print(f"--- Done ---")
        print(f"Called API {number_of_api_calls} times.")

