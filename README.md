# 🏛️ BoQ Material Passport Mapper

**Turn scanned, handwritten Bill of Quantities (BoQ) documents into clean, structured Material Passports — automatically.**

An AI-powered pipeline that reads construction BoQ PDFs (including handwritten annotations) and transforms them into industry-ready **Material Passport** Excel files. Built for civil, structural, and sustainability teams who need fast, accurate, and standardized material data — without manual data entry.

---

## 🌟 Why This Project

Bills of Quantities are often scanned, handwritten, and inconsistent — making them painful to digitize manually. This pipeline solves that by combining high-resolution document rasterization with GPT-4o's vision capabilities to reliably extract line items, material specifications, DSR/SOR codes, and project metadata, then maps everything directly into a standardized Material Passport template.

The result: **hours of manual tabulation reduced to a few automated steps**, with consistent, audit-ready output every time.

---

## ✨ Key Features

| Capability | Description |
|---|---|
| 📄 **High-Fidelity PDF Rasterization** | Renders each BoQ page at 200 DPI using `PyMuPDF`, preserving handwritten notes and table structure. |
| 🤖 **AI-Powered Extraction** | Uses `OpenAI GPT-4o` vision with strict `Pydantic` schema validation for reliable, structured output. |
| 🧱 **Automatic Metadata Capture** | Pulls handwritten project parameters (Plinth Area, Foundation Depth, Seismic Zone, Bearing Capacity) straight from Page 1. |
| 📏 **Smart Unit Normalization** | Standardizes inconsistent unit notation (`Cu.m → cum`, `Sq.m → sqm`) automatically. |
| 🗂️ **Direct Excel Schema Mapping** | Populates extracted data into the correct columns of an industry-aligned Material Passport template. |
| 📊 **Instant Visual Summary** | Generates extraction statistics and a material-category breakdown chart for quick review. |

---

## 🏗️ How It Works

```
BoQ PDF (scanned)
      │
      ▼
[1] pdf_to_images.py        →  temp_pages/page_*.jpeg   (200 DPI rasterization)
      │
      ▼
[2] src/extract.py          →  GPT-4o Vision + Pydantic
                                  ├─ output/building_meta.json
                                  ├─ output/raw_extracted.json
                                  └─ output/passport.json
      │
      ▼
[3] src/map_schema.py       →  output/passport_filled.xlsx  (AMP_Passport_Template.xlsx populated)
      │
      ▼
[4] src/visualize.py        →  output/material_distribution.png + console summary
```

Four clean stages — rasterize, extract, map, visualize — each producing a clear, inspectable output.

---

## 📁 Project Structure

```
boq-material-passport-mapper/
├── pdf_to_images.py              # Stage 1: PDF pages → JPEG images
├── src/
│   ├── extract.py                # Stage 2: GPT-4o based structured extraction
│   ├── map_schema.py             # Stage 3: JSON → Excel schema mapping
│   ├── visualize.py              # Stage 4: Summary stats + chart
│   └── __init__.py
├── AMP_Passport_Template.xlsx    # Target Material Passport Excel template
├── BoQ_CBRI_Principals_Residence.pdf   # Sample input BoQ
├── requirements.txt
├── APPROACH.md                   # Technical methodology writeup
└── .gitignore
```

---

## ⚙️ Getting Started

### 1. Clone the repository and set up a virtual environment
```bash
git clone <repo-url>
cd boq-material-passport-mapper
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your environment
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o
PDF_FILE_PATH=BoQ_CBRI_Principals_Residence.pdf
TEMP_PAGES_DIR=temp_pages
OUTPUT_DIR=output
EXCEL_TEMPLATE_PATH=AMP_Passport_Template.xlsx
```

You're all set — the pipeline is ready to run. 🎉

---

## ▶️ Usage

Run each stage in sequence:

```bash
# Step 1: Convert the PDF into page images
python pdf_to_images.py

# Step 2: Extract BoQ items and metadata using AI
python src/extract.py

# Step 3: Map the extracted data into the Excel template
python src/map_schema.py

# Step 4 (optional): Generate summary stats and a visual chart
python src/visualize.py
```

Each step is independent and inspectable — you can review intermediate JSON outputs before generating the final Excel file.

### 📦 Output Files (`output/` folder)

| File | Description |
|---|---|
| `building_meta.json` | Handwritten project metadata extracted from Page 1 |
| `raw_extracted.json` | Raw BoQ line items extracted from all pages |
| `passport.json` | Wrapped version of `raw_extracted.json` (`{"items": [...]}`) |
| `passport_filled.xlsx` | Final, populated Material Passport Excel file |
| `material_distribution.png` | Bar chart of items grouped by material category |

---

## 🔗 Excel Column Mapping

A quick reference for how extracted fields map into the Material Passport template:

| Extracted Field | Excel Column |
|---|---|
| `item_no` | Col 2 – BOQ Item No. |
| `description` | Col 5 – Element & Location |
| `floor_section` | Col 6 – Floor / Section |
| `discipline` | Col 7 – Discipline |
| `material_product` | Col 8 – Material |
| `material_category` | Col 10 – Material Category |
| `grade_mix` | Col 12 – Grade |
| `quantity` | Col 14 – Quantities |
| `unit` (normalized) | Col 15 – Original Unit |
| `dsr_code` | Col 27/28 – Schedule / Schedule Item Code |
| `rate` | Col 47 – Unit Rate |
| `amount` | Col 48 – Total Cost |
| — | Col 49 – Currency (fixed as `INR`) |

---

## 🧰 Tech Stack

- **AI Model** — OpenAI GPT-4o (Vision + structured output via `client.beta.chat.completions.parse`)
- **PDF Rendering** — PyMuPDF (`pymupdf`)
- **Schema Validation** — Pydantic
- **Excel Handling** — openpyxl
- **Data Analysis & Charting** — pandas, matplotlib
- **Configuration** — python-dotenv

---

## 🗺️ Roadmap

Ideas for where this project can go next:

- [ ] Support for multiple Material Passport templates and disciplines
- [ ] Confidence scoring surfaced per extracted field
- [ ] Batch processing for multi-project BoQ folders
- [ ] Web-based review UI for validating extracted items before export

Contributions and suggestions along these lines are very welcome!

---

## 🤝 Contributing

Improvements, bug fixes, and new ideas are welcome. Feel free to open an issue to discuss a change, or submit a pull request — this project is meant to grow with real-world BoQ formats and use cases.

---

## ⚠️ Notes & Limitations

- Extraction quality depends on handwriting clarity and scan resolution — clearer scans yield better results.
- A valid `OPENAI_API_KEY` is required for `src/extract.py` to run.
- If `passport_filled.xlsx` is already open elsewhere, the script automatically saves a fallback file named `passport_filled_updated.xlsx`, so no work is ever lost.
- Currently validated against a single Material Passport template (`AMP_Passport_Template.xlsx`) — broader template support is on the roadmap.

---

**Built to make material data digitization faster, cleaner, and a lot less manual.** 🚀
