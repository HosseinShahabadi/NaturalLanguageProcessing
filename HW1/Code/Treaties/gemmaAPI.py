import json
import lmstudio
import time
from QA import questions

# Connect to LM Studio
client = lmstudio.Client(api_host="172.20.67.136:1234")
m = client.llm.model('gemma-3-4b-persian-v0')

# print(m.respond("آخوند چیست؟").parsed)

# Load your JSON data
with open("qa_enriched_data.json", "r", encoding="utf-8") as f:
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

# Loop through data points and enrich using QA
for entry in data_list:
    text = entry.get("text", "")
    if not text.strip():
        continue  # Skip if there's no text to analyze

    for q in questions:
        field = q["field"]
        question_text = q["question"]

        try:
            print(f"Asking: {question_text}")
            answer = ask_question(question_text, text)
            print(answer)
            # You can do extra cleaning/parsing here if needed
            set_nested_field(entry, field, answer)
        except Exception as e:
            print(f"Failed to answer {field} for entry {entry.get('title', 'Unknown')}")
            print("Error:", e)
    
        time.sleep(0.2)

# Save the updated data
with open("qa_enriched_data_final.json", "w", encoding="utf-8") as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)
