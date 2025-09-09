import pandas as pd

# Load CSV file with UTF-8 encoding
csv_file = "product_summaries.csv"
df = pd.read_csv(csv_file, encoding="utf-8")

# Convert to JSON and save with UTF-8 encoding
json_file = "product_summaries.json"
df.to_json(json_file, orient="records", force_ascii=False, indent=4)

print(f"Converted {csv_file} to {json_file}")
