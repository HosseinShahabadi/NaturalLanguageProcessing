import json
import lmstudio
import time
from tqdm import tqdm
from QA import questions
import sys
import os

IP = "172.27.52.38:1234"

# Ensure UTF-8 output in terminal
sys.stdout.reconfigure(encoding='utf-8')

# Connect to LM Studio
client = lmstudio.Client(api_host=IP)
m = client.llm.model('gemma-3-4b-persian-v0')

# Load your JSON data
with open("iran_wars_with_details.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

def set_nested_field(data, field_path, value):
    """Set nested fields like 'period.start_year' inside the entry."""
    keys = field_path.split(".")
    for key in keys[:-1]:
        data = data.setdefault(key, {})
    data[keys[-1]] = value

def ask_question(question, context_text):
    """Send question to model with text context and get an answer."""
    return m.respond(f"{question}\n\nمتن:\n\"\"\"{context_text}\"\"\"").parsed

# tqdm setup
total_tasks = len(data_list) * len(questions)
progress_bar = tqdm(total=total_tasks, ncols=100, desc="Processing")

# limit = 10
# Enrich data
for entry_idx, entry in enumerate(data_list):
    # limit -= 1
    # if limit <= 0:
    #     break
    
    text = entry.get("text", "")
    if not text.strip():
        progress_bar.update(len(questions))
        continue  # Skip if there's no text to analyze

    for q in questions:
        field = q["field"]
        question_text = q["question"]

        try:
            # Move cursor up to print above the progress bar
            print('\033[K', end='')  # Clear the line
            print(f"\n[Entry {entry_idx+1}] Question: {question_text}")
            answer = ask_question(question_text, text)
            print(f"Answer: {answer}\n")
            set_nested_field(entry, field, answer)
        except Exception as e:
            print(f"❗ Failed to answer {field} for entry {entry.get('title', 'Unknown')}")
            print("Error:", e)

        progress_bar.update(1)
        time.sleep(0.02)
        
    question_text = "دو طرف این واقعه کدام کشورها هستند؟ فقط نام های آنان، جمله ننویس"
    print(f"\n[Entry {entry_idx+1}] Question: {question_text}")
    answer = ask_question(question_text, text)
    print(f"Answer: {answer}\n")
    

progress_bar.close()

# Save the updated data
with open("qa_enriched_data.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)
