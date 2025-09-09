import pandas as pd
import os

# --- Configuration ---
# This script selects products based on the highest rating count.

# Path to your dataset files
COMMENTS_FILE = './data/dropped_columns_comments.csv'
PRODUCTS_FILE = './data/dropped_columns_products.csv'

# The number of top unique products to select based on rating count
NUM_TOP_PRODUCTS_TO_SELECT = 2200

# Output file names
FILTERED_COMMENTS_FILE = 'top_rated_comments.csv'
FILTERED_PRODUCTS_FILE = 'top_rated_products.csv'


def select_top_rated_data(comments_df, products_df):
    """
    Selects the top N unique products based on their rating count ('Rate_cnt')
    and retrieves all associated comments. This version first de-duplicates
    the products list to ensure the selection is of unique products.

    Args:
        comments_df (pd.DataFrame): DataFrame containing all comments.
        products_df (pd.DataFrame): DataFrame containing all product details.

    Returns:
        tuple: A tuple containing two DataFrames:
               - final_comments_df: Filtered comments for the selected products.
               - final_products_df: Filtered product details for the selected products.
    """
    print("--- Starting Data Selection Based on Top Rated Products ---")

    # --- Step 1: De-duplicate the products dataframe ---
    print("\nRemoving duplicate product entries to work with unique products...")
    # We keep the first entry for each product_id to ensure uniqueness
    unique_products_df = products_df.drop_duplicates(subset=['id'], keep='first')
    print(f"Found {len(unique_products_df)} unique products in the source file.")

    # --- Step 2: Find the Top N Unique Products by Rating Count ---
    # We use .nlargest() on the de-duplicated dataframe.
    print(f"\nFinding the top {NUM_TOP_PRODUCTS_TO_SELECT} unique products by 'Rate_cnt'...")
    
    if 'Rate_cnt' not in unique_products_df.columns:
        print("Error: 'Rate_cnt' column not found in products file.")
        return pd.DataFrame(), pd.DataFrame()

    top_products_df = unique_products_df.nlargest(NUM_TOP_PRODUCTS_TO_SELECT, 'Rate_cnt')
    
    # Get the IDs of these top unique products
    top_product_ids = top_products_df['id'].unique()
    print(f"Selected {len(top_product_ids)} unique products.")

    # --- Step 3: Filter Comments for the Selected Products ---
    print("\nFiltering the comments file for the selected product IDs...")
    
    # Ensure product_id is the same integer type for matching
    comments_df.dropna(subset=['product_id'], inplace=True)
    comments_df['product_id'] = comments_df['product_id'].astype(int)
    
    # Perform the filtering
    final_comments_df = comments_df[comments_df['product_id'].isin(top_product_ids)].copy()

    # The final product list is the top_products_df we already found
    final_products_df = top_products_df.copy()

    print(f"\nFinal comments dataset shape: {final_comments_df.shape}")
    print(f"Final products dataset shape: {final_products_df.shape}")

    return final_comments_df, final_products_df


if __name__ == '__main__':
    if not os.path.exists(COMMENTS_FILE) or not os.path.exists(PRODUCTS_FILE):
        print(f"Error: Make sure '{COMMENTS_FILE}' and '{PRODUCTS_FILE}' are in the same directory.")
    else:
        print("Loading datasets...")
        # We only need to load the full comments file and the products file
        comments_df = pd.read_csv(COMMENTS_FILE)
        products_df = pd.read_csv(PRODUCTS_FILE)

        filtered_comments, filtered_products = select_top_rated_data(comments_df, products_df)

        if not filtered_comments.empty:
            print(f"\nSaving filtered data to '{FILTERED_COMMENTS_FILE}' and '{FILTERED_PRODUCTS_FILE}'...")
            filtered_comments.to_csv(FILTERED_COMMENTS_FILE, index=False, encoding='utf-8-sig')
            filtered_products.to_csv(FILTERED_PRODUCTS_FILE, index=False, encoding='utf-8-sig')
            print("\n--- Process Complete! ---")
