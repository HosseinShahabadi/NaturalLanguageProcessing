import json
import os

input_file = 'qa_enriched_data_final.json'
output_folder = 'data'

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the list of JSON objects
with open(input_file, 'r', encoding='utf-8') as f:
    json_list = json.load(f)

# Write each object into a separate JSON file inside the 'data' folder
for i, obj in enumerate(json_list, start=1):
    output_path = os.path.join(output_folder, f'{i}.json')
    with open(output_path, 'w', encoding='utf-8') as out_file:
        json.dump(obj, out_file, ensure_ascii=False, indent=2)
