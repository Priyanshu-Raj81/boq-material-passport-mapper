import os
import json
import glob
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class BoQItem(BaseModel):
    item_no: str = Field(description="Item or Schedule Number")
    description: str = Field(description="Detailed item work description")
    quantity: float | None = Field(default=None, description="Item quantity")
    unit: str | None = Field(default=None, description="Measurement unit (e.g., Cu.m, Sq.m, Each)")
    rate: float | None = Field(default=None, description="Item unit rate")
    amount: float | None = Field(default=None, description="Total computed amount")
    dsr_code: str | None = Field(default=None, description="DSR 1989 Code No or reference")

class BoQPageData(BaseModel):
    page_number: int
    items: list[BoQItem]

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def extract_boq_from_images():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing in .env file.")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    pages_dir = os.getenv("TEMP_PAGES_DIR", "temp_pages")

    image_paths = sorted(
        glob.glob(os.path.join(pages_dir, "page_*.jpeg")),
        key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0])
    )

    if not image_paths:
        raise FileNotFoundError(f"No images found in '{pages_dir}/'. Execute pdf_to_images.py first.")

    extracted_results = []

    prompt = (
        "Extract tabular entries from this Bill of Quantities (BoQ) page image into JSON.\n"
        "Fields to extract per row: Item No, Description, Quantity, Unit, Rate, Amount, DSR Code.\n"
        "Parse numeric fields strictly as clean numbers without units/currency strings."
    )

    for img_path in image_paths:
        page_num = int(os.path.basename(img_path).split('_')[1].split('.')[0])
        print(f"[*] Extracting data from Page {page_num} using {model_name}...")

        base64_img = encode_image_to_base64(img_path)

        response = client.beta.chat.completions.parse(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ],
                }
            ],
            response_format=BoQPageData,
            temperature=0.1
        )

        parsed_data = response.choices[0].message.parsed.model_dump()
        extracted_results.append(parsed_data)

    output_dir = os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)
    raw_json_path = os.path.join(output_dir, "raw_extracted.json")

    with open(raw_json_path, "w", encoding="utf-8") as f:
        json.dump(extracted_results, f, indent=2)

    print(f"[✓] Raw JSON successfully generated at '{raw_json_path}'")

if __name__ == "__main__":
    extract_boq_from_images()