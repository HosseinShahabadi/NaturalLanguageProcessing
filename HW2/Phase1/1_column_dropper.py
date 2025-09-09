import pandas as pd


COMMENTS_FILE = './data/digikala-comments.csv'
PRODUCTS_FILE = './data/digikala-products.csv'

# Output file names
DROPPED_COMMENTS_FILE = 'dropped_columns_comments.csv'
DROPPED_PRODUCTS_FILE = 'dropped_columns_products.csv'

comments_cols_to_drop = ['created_at', 'is_buyer', 'seller_title', 'seller_code', 'true_to_size_rate']
products_cols_to_drop = ['Category2', 'Price', 'Seller', 'Is_Fake', 'min_price_last_month', 'sub_category']

try:
    comments_df = pd.read_csv(COMMENTS_FILE, usecols=lambda col: col not in comments_cols_to_drop)
    products_df = pd.read_csv(PRODUCTS_FILE, usecols=lambda col: col not in products_cols_to_drop)


    comments_df.to_csv(DROPPED_COMMENTS_FILE, index=False, encoding='utf-8-sig')
    products_df.to_csv(DROPPED_PRODUCTS_FILE, index=False, encoding='utf-8-sig')
    print(f"Done.")

except FileNotFoundError:
    print(f"Error: The file '{COMMENTS_FILE}' or '{PRODUCTS_FILE}' was not found.")

