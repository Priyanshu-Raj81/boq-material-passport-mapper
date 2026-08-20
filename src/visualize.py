import os
import json
import matplotlib.pyplot as plt
import pandas as pd

def generate_visualization():
    output_dir = os.getenv("OUTPUT_DIR", "output")
    json_path = os.path.join(output_dir, "raw_extracted.json")

    if not os.path.exists(json_path):
        print(f"[!] Error: {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    df = pd.DataFrame(items)
    
    print("=" * 45)
    print("       BOQ EXTRACTION SUMMARY VISUALIZER     ")
    print("=" * 45)
    print(f"Total Extracted Line Items: {len(df)}")
    print(f"Items with Quantities:      {df['quantity'].notna().sum()}")
    print(f"Items with DSR Codes:       {df['dsr_code'].notna().sum()}")
    print("=" * 45)

    # Generate Chart if categories exist
    plt.figure(figsize=(10, 5))
    if 'material_category' in df.columns and df['material_category'].notna().any():
        counts = df['material_category'].value_counts()
        counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Extracted Items by Material Category')
        plt.xlabel('Category')
        plt.ylabel('Item Count')
        plt.tight_layout()
        chart_path = os.path.join(output_dir, "material_distribution.png")
        plt.savefig(chart_path)
        print(f"[✓] Material distribution chart saved to '{chart_path}'")

if __name__ == "__main__":
    generate_visualization()