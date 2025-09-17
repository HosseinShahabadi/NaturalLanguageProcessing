import os
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Function to recursively collect all JSON files
def get_all_json_files(root_dir):
    return list(Path(root_dir).rglob("*.json"))

# Helper to safely load JSON
def load_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Root directory containing folders of JSON files
ROOT_DIR = "./datasets"

# Load all JSONs
all_data = []
json_files = get_all_json_files(ROOT_DIR)

for file in json_files:
    data = load_json_file(file)
    if data:
        # Handle both list of dicts and single dict
        if isinstance(data, list):
            all_data.extend(data)
        else:
            all_data.append(data)

# Flatten the JSONs to DataFrame (pandas will handle nested keys with dot notation)
df = pd.json_normalize(all_data)

# Save combined data (optional)
df.to_csv("combined_dataset.csv", index=False)

# Sample stats
print("🔢 تعداد نمونه‌ها:", len(df))

# --- Word/char stats like before ---
def word_count(text):
    if isinstance(text, str):
        return len(text.split())
    return 0

def char_length(text):
    if isinstance(text, str):
        return len(text)
    return 0

# Analyze all string/text fields
text_fields = df.select_dtypes(include='object').columns
field_stats = {}

for field in text_fields:
    field_data = df[field].dropna().astype(str)
    total_words = field_data.apply(word_count).sum()
    avg_chars = field_data.apply(char_length).mean()
    field_stats[field] = {"total_words": total_words, "avg_chars": avg_chars}

# Summary
total_words_all_fields = sum(fs["total_words"] for fs in field_stats.values())

# Prepare output text
output_lines = []

output_lines.append(f"Total number of samples: {len(df)}\n")
output_lines.append(f"Total number of words in all fields: {total_words_all_fields}\n")

output_lines.append("\n📊 Text Field Statistics:")
for field, stats in field_stats.items():
    output_lines.append(f"\nField: {field}")
    output_lines.append(f"  - Total words: {stats['total_words']}")
    output_lines.append(f"  - Average string length (characters): {stats['avg_chars']:.2f}")

# Print to console
for line in output_lines:
    print(line)

# Save to text file
with open("dataset_statistics.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

# ---------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure seaborn style
sns.set(style="whitegrid")

# Extract data for plots
fields = list(field_stats.keys())
word_totals = [stats["total_words"] for stats in field_stats.values()]
avg_chars = [stats["avg_chars"] for stats in field_stats.values()]

# Plot: Total Words per Field
plt.figure(figsize=(12, 6))
sns.barplot(x=word_totals, y=fields, palette="viridis")
plt.title("Total Words per Field")
plt.xlabel("Total Words")
plt.ylabel("Field")
plt.tight_layout()
plt.savefig("total_words_per_field.png")
plt.show()

# Plot: Average String Length per Field
plt.figure(figsize=(12, 6))
sns.barplot(x=avg_chars, y=fields, palette="magma")
plt.title("Average String Length (Characters) per Field")
plt.xlabel("Average Characters")
plt.ylabel("Field")
plt.tight_layout()
plt.savefig("avg_chars_per_field.png")
plt.show()
