import json

with open("image caption.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("image caption.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
