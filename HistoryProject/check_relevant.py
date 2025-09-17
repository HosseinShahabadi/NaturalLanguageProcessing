import os
import sys
import subprocess
import urllib.parse
from tqdm import tqdm
import json
import time
from API import ApiClient

# Try to import wikipedia, install if missing
try:
    import wikipedia
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "wikipedia"])
    import wikipedia

LLM_PROMPT_TEMPLATE = """
You are a classifier. Your task is to decide if the following Wikipedia article text is
DIRECTLY related to the **history of Iran** (wars, battles, dynasties, rulers, events,
or military/political history).

Important rules:
- Answer `1` if it is directly related to Iran.
- Answer `0` if it is not related, or if it is only about neighbors (e.g. Ottoman Empire, Rome, Russia, Greece) without direct Iranian involvement.
- Do not explain. Do not output anything else besides 0 or 1.

Text:
----------------
{content}
----------------

Your answer (only 0 or 1):
"""

MAX_DATASET_SIZE = 10000  # stop after saving this many relevant contents

INPUT_FILE = f"./part_5to7.txt"
OUTPUT_FILE = "./Dataset/part_5to7.json"
DATASET_DIR = "./Dataset/Dataset_part_5to7"

os.makedirs(DATASET_DIR, exist_ok=True)

# ---------------------------
# Helper functions
# ---------------------------
def load_existing():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return {r["url"]: r["is_related"] for r in json.load(f)}
    return {}

def save_results(new_results):
    existing_results = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass  # Corrupted file; start fresh

    # Merge: Update or append new_results (assuming new_results is full list)
    url_to_idx = {r["url"]: i for i, r in enumerate(existing_results)}
    for nr in new_results:
        if nr["url"] in url_to_idx:
            existing_results[url_to_idx[nr["url"]]] = nr  # Update
        else:
            existing_results.append(nr)  # Append

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_results, f, ensure_ascii=False, indent=2)

def fetch_wikipedia_content(url: str) -> str:
    """Try to extract and fetch page content from a Farsi Wikipedia URL."""
    page_title = urllib.parse.unquote(url.split("/wiki/")[1].replace("_", " "))
    page_title_clean = page_title.replace(" (شاهنشاه هخامنشی)", "")
    search_queries = [
        page_title,
        page_title_clean,
        (
            page_title_clean.split()[0] + " " + page_title_clean.split()[1]
            if len(page_title_clean.split()) > 1
            else page_title_clean
        ),
    ]

    wikipedia.set_lang("fa")
    for query in search_queries:
        try:
            wikipedia.set_lang("fa")
            results = wikipedia.search(query)
            if results:
                page = wikipedia.page(results[0])
                return page.content
        except Exception:
            continue
    return ""

def is_relevant(content: str, threshold: int = 700) -> bool:
    """Decide if the Wikipedia page is relevant using content length + LLM."""
    if len(content) < threshold:
        return False  # too short, likely stub

    # prompt = LLM_PROMPT_TEMPLATE.format(content=content[:10000])
    # outputs = generator(prompt, max_new_tokens=5, do_sample=False)  # Limit to short response; deterministic for yes/no
    # full_text = outputs[0]["generated_text"]
    # generated_only = full_text[len(prompt):].strip()  # Extract only new tokens after prompt
    # print(generated_only)  # Now prints just the LLM answer (e.g., "1")
    # return generated_only == "1"
    prompt = LLM_PROMPT_TEMPLATE.format(content=content[:10000])
    outputs = get_summary_from_api(prompt)
    # full_text = outputs[0]["generated_text"]
    # full_text = outputs
    # print(full_text)
    # generated_only = full_text[len(prompt):].strip()  # Extract only new tokens after prompt
    # print(generated_only)  # Now prints just the LLM answer (e.g., "1")
    return outputs == "1"

def get_summary_from_api(prompt, retries=3, delay=5):
    """
    Calls the OpenAI API to get a summary for a block of comments.
    Includes basic retry logic for handling transient API errors.
    """
    for attempt in range(retries):
        try:
            return Client._request(prompt)
        except Exception as e:
            print(f"API call failed on attempt {attempt + 1}/{retries}. Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Skipping this Data Point.")
                return f"Error: API call failed after {retries} retries."

# ---------------------------
# Main pipeline
# ---------------------------
def main():
    processed = load_existing()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    urls = unique_urls

    results = [{"url": url, "is_related": processed.get(url, None)} for url in urls]

    # figure out how many we already saved in Dataset
    dataset_id = len(os.listdir(DATASET_DIR)) + 1
    true_count, false_count = 0, 0

    with tqdm(total=len(urls), desc="Processing", unit="url") as pbar:
        for entry in results:
            # ✅ stop early when we hit K
            if dataset_id > MAX_DATASET_SIZE:
                print(f"✅ Reached {MAX_DATASET_SIZE} relevant pages, stopping early.")
                break

            url = entry["url"]
            if entry["is_related"] is None:
                content = fetch_wikipedia_content(url)

                if not content:
                    entry["is_related"] = False
                else:
                    entry["is_related"] = is_relevant(content)

                    if entry["is_related"]:
                        true_count += 1
                        file_path = os.path.join(DATASET_DIR, f"{dataset_id}.txt")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        dataset_id += 1
                    else:
                        false_count += 1

                save_results(results)
            else:
                if entry["is_related"]:
                    true_count += 1
                else:
                    false_count += 1

            pbar.set_postfix({"True": true_count, "False": false_count})
            pbar.update(1)

    save_results(results)


if __name__ == "__main__":
    Client = ApiClient()
    main()
