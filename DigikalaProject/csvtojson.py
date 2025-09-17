import csv
import json

# --- Configuration ---
CSV_FILE = "digikala_products.csv"
JSON_FILE = "digikala_products.json"

def create_json_from_csv():
    """Reads digikala_general_products.csv, filters entries, and creates a JSON file."""
    data = []
    
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['comments_overview'] != 'NULL':
                entry = {
                    "product_id": row['id'],
                    "title_fa": row['title_fa'],
                    "title_en": row['title_en'],
                    "summary": row['comments_overview'],
                    "is_overview": True
                }
                data.append(entry)
            elif row['introduction'] != 'N/A':
                entry = {
                    "product_id": row['id'],
                    "title_fa": row['title_fa'],
                    "title_en": row['title_en'],
                    "summary": row['introduction'],
                    "is_overview": False
                }
                data.append(entry)
    
    with open(JSON_FILE, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
    
    print(f"Created {JSON_FILE} with {len(data)} entries.")

if __name__ == "__main__":
    create_json_from_csv()
