import json
import os

# Path to your main JSON file
input_file = 'iran_histroy_with_details_final.json'

# Output directory to save separated JSON files
output_dir = 'output_files'
os.makedirs(output_dir, exist_ok=True)

# Load the data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Split and save each datapoint
for idx, datapoint in enumerate(data, start=1):  # <-- start=1 here
    output_path = os.path.join(output_dir, f"{idx}.json")
    with open(output_path, 'w', encoding='utf-8') as out_f:
        json.dump(datapoint, out_f, ensure_ascii=False, indent=4)

print(f"Done! Saved {len(data)} files in '{output_dir}' folder starting from 1.")
