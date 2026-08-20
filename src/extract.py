import os
import json
import base64
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ExtractedBoQItem(BaseModel):
    item_no: Optional[str] = Field(default=None, description="BOQ Item Number or Serial Number")
    dsr_code: Optional[str] = Field(default=None, description="DSR / SOR Code e.g. 2.35.2 or 5.22.6")
    description: str = Field(description="Full text description of the BOQ item")
    floor_section: Optional[str] = Field(default=None, description="Sub-head or section e.g. Earthwork, RCC Work, Finishing")
    discipline: Optional[str] = Field(default=None, description="Civil, Structural, Architectural, MEP, etc.")
    material_product: Optional[str] = Field(default=None, description="Primary material e.g. Cement, TMT Steel, Fine Sand, Bricks")
    material_category: Optional[str] = Field(default=None, description="Category e.g. Concrete, Steel, Earthwork, Masonry")
    grade_mix: Optional[str] = Field(default=None, description="Grade or mix ratio e.g. Fe-500D, M20, 1:2:4, 1:4")
    quantity: Optional[float] = Field(default=None, description="Numerical quantity parsed from text/handwriting")
    unit: Optional[str] = Field(default=None, description="Normalized unit: cum, sqm, m, kg, quintal, nos")
    rate: Optional[float] = Field(default=None, description="Unit rate if present")
    amount: Optional[float] = Field(default=None, description="Total amount if present")

class BoQPageData(BaseModel):
    page_number: int
    items: List[ExtractedBoQItem]

class BuildingMetadata(BaseModel):
    project_name: Optional[str] = None
    plinth_area: Optional[str] = None
    foundation_depth: Optional[str] = None
    seismic_zone: Optional[str] = None
    bearing_capacity: Optional[str] = None

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_building_meta(image_path: str) -> BuildingMetadata:
    base64_img = encode_image(image_path)
    prompt = "Extract handwritten building metadata parameters from Page 1: Plinth Area, Foundation Depth, Seismic Zone, Bearing Capacity, and Project Name."
    
    response = client.beta.chat.completions.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]}
        ],
        response_format=BuildingMetadata,
    )
    return response.choices[0].message.parsed

def process_all_pages():
    temp_dir = os.getenv("TEMP_PAGES_DIR", "temp_pages")
    output_dir = os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)

    image_files = sorted(
        [f for f in os.listdir(temp_dir) if f.startswith("input_file_") or f.startswith("page_")],
        key=lambda x: int(x.split('_')[-1].split('.')[0])
    )

    all_extracted_items = []

    # Process Page 1 metadata
    if image_files:
        print("[+] Extracting building metadata from Page 1...")
        meta = extract_building_meta(os.path.join(temp_dir, image_files[0]))
        with open(os.path.join(output_dir, "building_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta.model_dump(), f, indent=2)

    for idx, img_name in enumerate(image_files, start=1):
        img_path = os.path.join(temp_dir, img_name)
        print(f"[+] Processing {img_name} ({idx}/{len(image_files)})...")
        base64_img = encode_image(img_path)

        response = client.beta.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert civil engineer and BoQ data extractor. Extract tabular line items accurately from scanned images. Normalize units (e.g., Cu.m -> cum, Sq.m -> sqm). Detect DSR codes, materials, disciplines, and grades."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract all BoQ items from this page image into structured format."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]}
            ],
            response_format=BoQPageData,
        )
        
        parsed_data = response.choices[0].message.parsed
        for item in parsed_data.items:
            all_extracted_items.append(item.model_dump())

    # Save to raw JSON and passport.json
    with open(os.path.join(output_dir, "raw_extracted.json"), "w", encoding="utf-8") as f:
        json.dump(all_extracted_items, f, indent=2)
    
    with open(os.path.join(output_dir, "passport.json"), "w", encoding="utf-8") as f:
        json.dump({"items": all_extracted_items}, f, indent=2)

    print(f"[✓] Extraction complete. Total {len(all_extracted_items)} items saved.")

if __name__ == "__main__":
    process_all_pages()