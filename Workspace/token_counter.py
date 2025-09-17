import pandas as pd
import tiktoken
import os
import numpy as np  # Added for statistical calculations

# --- Configuration ---

# The CSV file containing the comments you want to analyze.
# This should be the output from your previous data selection script.
COMMENTS_FILE = './digikala_products.csv'
# COMMENTS_FILE = './tokentest.csv'

# The columns that contain the text you plan to send to the model.
TEXT_COLUMNS = ['comments_overview']

# The encoding model to use. 'cl100k_base' is the standard for GPT-3.5-Turbo and GPT-4 models.
# This provides a very accurate estimate for models like gpt-4.1-mini.
ENCODING_NAME = 'cl100k_base'

# Optional: Add a cost per million tokens to estimate API expenses.
# This is a hypothetical cost; check the latest OpenAI pricing for accuracy.
# For example, $0.15 per 1 million input tokens.
COST_PER_MILLION_TOKENS = 0.44


def count_tokens_in_csv(file_path):
    """
    Reads a CSV file, counts the tokens in specified text columns for all rows,
    provides statistics (min, max, avg token count per row), and an estimated cost.

    Args:
        file_path (str): The path to the CSV file.
    """
    print(f"--- Token Counter Initialized ---")
    
    # --- Step 1: Load the tokenizer ---
    try:
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        print(f"Using '{ENCODING_NAME}' encoding.")
    except Exception as e:
        print(f"Error getting tokenizer: {e}")
        print("Please make sure you have the 'tiktoken' library installed: pip install tiktoken")
        return

    # --- Step 2: Load the dataset ---
    print(f"Loading comments from '{file_path}'...")
    try:
        df = pd.read_csv(file_path)  # Removed nrows=1 to read all rows
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please run the data selection script first to generate this file.")
        return

    token_counts = []  # List to store token counts per row
    
    # --- Step 3: Iterate and count tokens ---
    print(f"Counting tokens in columns: {', '.join(TEXT_COLUMNS)}...")
    
    for index, row in df.iterrows():
        row_tokens = 0
        for col in TEXT_COLUMNS:
            # Get the text, handle potential missing values (NaNs)
            text = row.get(col)
            if isinstance(text, str):
                # Encode the text and add the number of tokens to the row total
                row_tokens += len(encoding.encode(text))
        token_counts.append(row_tokens)

    total_tokens = sum(token_counts)
    
    print("\n--- Results ---")
    print(f"Total rows processed: {len(token_counts)}")
    print(f"Total tokens calculated: {total_tokens:,}")

    if token_counts:
        min_tokens = min(token_counts)
        max_tokens = max(token_counts)
        avg_tokens = np.mean(token_counts)
        print(f"Min tokens per row: {min_tokens:,}")
        print(f"Max tokens per row: {max_tokens:,}")
        print(f"Average tokens per row: {avg_tokens:,.2f}")

    # --- Step 4: Estimate the cost ---
    if COST_PER_MILLION_TOKENS > 0:
        estimated_cost = (total_tokens / 1_000_000) * COST_PER_MILLION_TOKENS
        print(f"Estimated API Cost: ${estimated_cost:.4f} (at ${COST_PER_MILLION_TOKENS}/1M tokens)")


if __name__ == '__main__':
    # Before running, ensure you have the required library installed:
    # pip install pandas tiktoken numpy
    
    if not os.path.exists(COMMENTS_FILE):
        print(f"Error: The input file '{COMMENTS_FILE}' was not found in this directory.")
    else:
        count_tokens_in_csv(COMMENTS_FILE)
