import os
import json

BASE_DIR = "./ProcessedImages"
JSON_PATH = "./Pairs/Texts.json"

ALLOWED_EXT = {"png", "jpg", "jpeg"}

# --- Load JSON ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to dict for quick id lookup
data_dict = {str(item["id"]): item for item in data}

# --- Process folders ---
for folder in os.listdir(BASE_DIR):
    folder_path = os.path.join(BASE_DIR, folder)
    if not os.path.isdir(folder_path):
        continue  # skip if not a folder
    
    # Keep only allowed images
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if not os.path.isfile(file_path):
            continue

        ext = file.split(".")[-1].lower()
        if ext not in ALLOWED_EXT:
            print(f"Deleting file: {file_path}")
            os.remove(file_path)

    # After cleanup, check if folder is empty
    if not os.listdir(folder_path):
        print(f"Deleting empty folder: {folder_path}")
        os.rmdir(folder_path)

        # Remove from JSON if id exists
        if folder in data_dict:
            print(f"Removing id {folder} from JSON")
            del data_dict[folder]

# --- Save updated JSON ---
new_data = list(data_dict.values())
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print("Cleanup complete ✅")
