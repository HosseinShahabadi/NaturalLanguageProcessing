import pandas as pd
import os

# --- Configuration ---

# The input file from the previous step.
INPUT_COMMENTS_FILE = './top_rated_comments.csv'

# The final output file containing only the longest comments.
OUTPUT_COMMENTS_FILE = 'longest_comments_for_top_rated_products.csv'

# The number of longest comments to keep for each product.
NUM_COMMENTS_TO_KEEP = 50

# The column to use for measuring comment length. 'body' is usually the most descriptive.
LENGTH_COLUMN = 'body'


def filter_longest_comments(input_file):
    """
    Reads a comments CSV, and for each product, keeps only the N longest comments.

    Args:
        input_file (str): Path to the input CSV file.
    
    Returns:
        pd.DataFrame: A new dataframe with the filtered comments.
    """
    print("--- Filtering for Longest Comments ---")

    # --- Step 1: Load the dataset ---
    print(f"Loading comments from '{input_file}'...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        print("Please make sure you have run the previous data selection script.")
        return pd.DataFrame()

    # --- Step 2: Calculate comment length ---
    # We'll create a temporary column to hold the length of the text.
    # We fill NaN values with an empty string to avoid errors and give them a length of 0.
    print(f"Calculating length of comments based on the '{LENGTH_COLUMN}' column...")
    df['comment_length'] = df[LENGTH_COLUMN].fillna('').str.len()

    # --- Step 3: Group by product and select top N longest comments ---
    print(f"Grouping by product and selecting the top {NUM_COMMENTS_TO_KEEP} longest comments for each...")
    
    # We use groupby() on 'product_id' and then apply a function to each group.
    # The function sorts the group by 'comment_length' and takes the top N.
    filtered_df = df.groupby('product_id').apply(
        lambda x: x.nlargest(NUM_COMMENTS_TO_KEEP, 'comment_length')
    ).reset_index(drop=True)

    # --- Step 4: Clean up and final checks ---
    # The temporary 'comment_length' column is no longer needed.
    filtered_df = filtered_df.drop(columns=['comment_length'])

    print("\n--- Results ---")
    print(f"Original number of comments: {len(df):,}")
    print(f"Filtered number of comments: {len(filtered_df):,}")
    
    return filtered_df


if __name__ == '__main__':
    if not os.path.exists(INPUT_COMMENTS_FILE):
        print(f"Error: The input file '{INPUT_COMMENTS_FILE}' was not found.")
    else:
        final_comments = filter_longest_comments(INPUT_COMMENTS_FILE)

        if not final_comments.empty:
            print(f"\nSaving filtered data to '{OUTPUT_COMMENTS_FILE}'...")
            final_comments.to_csv(OUTPUT_COMMENTS_FILE, index=False, encoding='utf-8-sig')
            print("\n--- Process Complete! ---")
            print("Your new dataset with only the longest comments is ready.")

