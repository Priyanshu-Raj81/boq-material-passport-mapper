import os
import json
import glob
import openpyxl
from dotenv import load_dotenv

load_dotenv()

def map_data_to_excel_template():
    output_dir = os.getenv("OUTPUT_DIR", "output")
    json_path = os.path.join(output_dir, "raw_extracted.json")
    excel_template = os.getenv("EXCEL_TEMPLATE_PATH", "AMP_Passport_Template_2.xlsx")
    final_excel_path = os.path.join(output_dir, "passport_filled.xlsx")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Extraction file missing at: {json_path}")

    if not os.path.exists(excel_template):
        xlsx_files = [f for f in glob.glob("*.xlsx") if not f.startswith("~$") and f != "passport_filled.xlsx"]
        if xlsx_files:
            excel_template = xlsx_files[0]
        else:
            raise FileNotFoundError("No Excel template (.xlsx) found!")

    wb = openpyxl.load_workbook(excel_template)
    ws = wb.active

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Clean dummy example rows (Rows 4 and 5)
    for r in range(4, 6):
        for c in range(1, 51):
            ws.cell(row=r, column=c).value = None

    start_row = 4

    for page in raw_data:
        for item in page.get("items", []):
            item_no = item.get("item_no", "")
            description = item.get("description", "")
            dsr_code = item.get("dsr_code", "")
            quantity = item.get("quantity", None)
            unit = item.get("unit", "")
            rate = item.get("rate", None)
            amount = item.get("amount", None)

            # Mapping to AMP Material Passport Template Schema
            ws.cell(row=start_row, column=2, value=item_no)        # Col B: BOQ Item No.
            ws.cell(row=start_row, column=4, value=dsr_code)       # Col D: External DB Id / DSR Code
            ws.cell(row=start_row, column=5, value=description)    # Col E: Description
            
            if quantity is not None:
                ws.cell(row=start_row, column=14, value=quantity)  # Col N: Original Quantity
            
            if unit:
                ws.cell(row=start_row, column=15, value=unit)      # Col O: Original Unit
                
            if rate is not None:
                ws.cell(row=start_row, column=47, value=rate)      # Col AU: Unit Rate
                
            if amount is not None:
                ws.cell(row=start_row, column=48, value=amount)    # Col AV: Total Cost
                
            ws.cell(row=start_row, column=49, value="INR")          # Col AW: Currency

            start_row += 1

    wb.save(final_excel_path)
    print(f"[✓] Successfully populated full schema into '{final_excel_path}'")

if __name__ == "__main__":
    map_data_to_excel_template()