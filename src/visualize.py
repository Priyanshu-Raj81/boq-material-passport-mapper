import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def generate_extraction_summary():
    output_dir = os.getenv("OUTPUT_DIR", "output")
    json_path = os.path.join(output_dir, "raw_extracted.json")

    if not os.path.exists(json_path):
        print("[!] No extracted JSON found to summarize.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    total_pages = len(raw_data)
    total_items = sum(len(page.get("items", [])) for page in raw_data)

    print("\n" + "="*40)
    print("      EXTRACTION SUMMARY PIPELINE     ")
    print("="*40)
    print(f"Total Pages Processed : {total_pages}")
    print(f"Total BoQ Items Found : {total_items}")
    print("="*40 + "\n")

if __name__ == "__main__":
    generate_extraction_summary()