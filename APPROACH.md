# 🏛️ Approach & Technical Methodology

## 1. Architecture Overview
This pipeline transforms unstructured scanned BoQ PDFs into structured Material Passports using an end-to-end multi-stage architecture:

1. **Rasterization Stage:** High-resolution page rendering (200 DPI) via `PyMuPDF` to preserve handwritten annotations and tabular layout.
2. **AI Extraction Stage:** Multi-modal extraction using `OpenAI GPT-4o` with strict `Pydantic` schema enforcement (`client.beta.chat.completions.parse`).
3. **Unit Normalization & Validation:** Automated standardizing of unit strings (`Cu.m` -> `cum`, `Sq.m` -> `sqm`).
4. **Schema Alignment:** Structured mapping into Excel (`AMP_Passport_Template.xlsx`), populating critical green-tier Material Passport columns.

## 2. DSR Code & Material Mapping Strategy
- DSR Item Codes are explicitly identified and mapped to **Column 28 (`Schedule Item Code`)** and tagged under **Column 27 (`Schedule`)**.
- Contextual classification maps material descriptions to `Discipline`, `Material Category`, and `Grade/Mix Ratio`.

## 3. Metadata Extraction
Page 1 contains handwritten engineering parameters (Plinth Area, Foundation Depth, Seismic Zone, Bearing Capacity) which are parsed separately into `building_meta.json`.