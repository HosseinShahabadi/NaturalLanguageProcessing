import json
import re

def format_list_field(field):
    if isinstance(field, str):
        # If "\n" or "*\n" exists, process it into a list
        if '\n' in field or '*\n' in field:
            field = field.replace('*', '')        # Remove all '*'
            cleaned = re.sub(r'\n', ',', field)    # Replace "\n" with ","
            parts = [part.strip() for part in cleaned.split(',') if part.strip()]
            return parts
        else:
            # Otherwise, just remove '*' and return the cleaned string
            return field.replace('*', '').strip()
    return field


# Load the JSON file
with open('iran_treaties_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fields you want to apply formatting to
fields_to_format = ["description", "causes", "belligerents", "result", "impact", "historical_significance"]

# Process each datapoint
for item in data:
    # Remove unwanted fields
    item.pop('text', None)
    item.pop('historical_siginificance', None)  # Careful about the misspelling

    # Format main fields
    for field in fields_to_format:
        if field in item:
            item[field] = format_list_field(item[field])

    # Format nested field 'location.city'
    if 'location' in item and 'city' in item['location']:
        item['location']['city'] = format_list_field(item['location']['city'])

    # Now remove '*' from all remaining string fields in the item
    def remove_stars(obj):
        if isinstance(obj, dict):
            return {k: remove_stars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [remove_stars(elem) for elem in obj]
        elif isinstance(obj, str):
            return obj.replace('*', '')
        else:
            return obj

    item = remove_stars(item)

# Save to a new file
with open('iran_histroy_with_details_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Finished cleaning, formatting, and removing '*' from the JSON file.")
