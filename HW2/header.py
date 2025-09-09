import pandas as pd


COMMENTS_FILE = './data/digikala-comments.csv'
PREVIEW_COMMENTS_FILE = 'preview_comments.csv'

try:
    df_preview = pd.read_csv(COMMENTS_FILE, nrows=5)

    print("Column Headers:")
    print(list(df_preview.columns))

    print("\nFirst 5 Rows:")
    print(df_preview)

    df_preview.to_csv(PREVIEW_COMMENTS_FILE, index=False, encoding='utf-8-sig')

except FileNotFoundError:
    print(f"Error: The file '{COMMENTS_FILE}' was not found.")

