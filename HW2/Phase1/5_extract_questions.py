import pandas as pd
import os
import time
import json
from openai import OpenAI
from tqdm import tqdm

# --- Configuration ---

# 1. API KEY SETUP
# Ensure the OPENAI_API_KEY environment variable is set.
api_key = os.getenv("OPENAI_API_KEY")

# URL = "https://api.metisai.ir/openai/v1"
URL = "https://api.gapgpt.app/v1"

MODEL_NAME = "gpt-4.1-mini"  # The model you requested
MAX_TOKENS_FOR_QUESTIONS = 500 # A bit of buffer over 450

# 2. FILE AND MODEL SETTINGS
INPUT_FILE = 'product_summaries.csv'
PRODUCTS_INFO_FILE = './data/dropped_columns_products.csv'
# The output is now a JSON file
OUTPUT_FILE = 'product_questions.json'

# --- API Client Class (re-used for consistency) ---
class ApiClient:
    def __init__(self):
        self.model = MODEL_NAME
        self.client = OpenAI(
            base_url=URL,
            api_key=os.getenv("OPENAI_API_KEY") 
        )

    def _request(self, prompt):
        if not self.client.api_key:
            return "Error: API key not configured."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS_FOR_QUESTIONS,
                temperature=0.4 # A bit more creative for question generation
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An API error occurred: {e}"

# --- Prompt Template for Question Generation ---
PROMPT_TEMPLATE = """
From the Persian text provided below, generate between 5 and 7 unique questions in Persian.
Each question must target a different piece of information within the text.
All questions must be answerable solely based on the given text.
IMPORTANT: Do not number the questions. Separate each question with a new line.

Text:
---
{summary_text}
---

Questions:
"""

def get_questions_from_api(summary_text, retries=3, delay=5):
    """
    Calls the API to generate questions for a given summary.
    """
    prompt = PROMPT_TEMPLATE.format(summary_text=summary_text)
    for attempt in range(retries):
        try:
            response_text = Client._request(prompt)
            questions = [q.strip() for q in response_text.split('\n') if q.strip()]
            if "An API error occurred" in response_text:
                raise Exception(response_text)
            return questions
        except Exception as e:
            print(f"API call failed on attempt {attempt + 1}/{retries}. Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this summary.")
                return [f"Error: Could not generate questions."]


def generate_questions():
    """
    Main function to orchestrate the question generation process.
    """
    print("--- Starting Question Generation (JSON Output) ---")
    
    try:
        df = pd.read_csv(INPUT_FILE)
        products_df = pd.read_csv(PRODUCTS_INFO_FILE)
    except FileNotFoundError as e:
        print(f"Error: Could not find an input file: {e}")
        return

    # --- Create a lookup map for product titles for efficiency ---
    # This converts the dataframe into a dictionary for fast lookups.
    product_title_map = pd.Series(products_df.title_fa.values, index=products_df.id).to_dict()

    # --- Resume Logic for JSON ---
    if os.path.exists(OUTPUT_FILE):
        print(f"Found existing output file: '{OUTPUT_FILE}'. Resuming.")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            results_list = json.load(f)
        processed_ids = [item['product_id'] for item in results_list]
    else:
        results_list = []
        processed_ids = []

    # Filter out already processed products
    df_to_process = df[~df['product_id'].isin(processed_ids)]

    if df_to_process.empty:
        print("All product summaries have already been processed. Process complete.")
        return

    # --- Main Loop ---
    print(f"Found {len(df_to_process)} new product summaries to process.")
    for index, row in tqdm(df_to_process.iterrows(), total=df_to_process.shape[0], desc="Generating Questions"):
        product_id = row['product_id']
        summary = row['summary']

        if not isinstance(summary, str) or summary.startswith("Error:"):
            print(f"Skipping Product ID {product_id} due to invalid summary.")
            continue
        
        questions = get_questions_from_api(summary)
        
        # Get the product title from our lookup map
        product_title = product_title_map.get(product_id, "Title Not Found")

        # --- Append the new data in the desired JSON structure ---
        results_list.append({
            'product_id': int(product_id),
            'title_fa': product_title, # Added the title here
            'summary': summary,
            'questions': questions
        })

        # --- Save Progress to JSON file ---
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # ensure_ascii=False is crucial for saving Persian characters correctly
            json.dump(results_list, f, ensure_ascii=False, indent=4)

    print("\n--- Process Complete! ---")
    print(f"All questions have been generated and saved to '{OUTPUT_FILE}'.")


if __name__ == '__main__':
    if not api_key:
        print("FATAL ERROR: OpenAI API key is not configured.")
    else:
        print("✅ API Key found successfully.")

        Client = ApiClient()
        generate_questions()
