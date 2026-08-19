import os
import glob
import pymupdf
from dotenv import load_dotenv

load_dotenv()

def convert_pdf_to_images():
    pdf_path = os.getenv("PDF_FILE_PATH", "BoQ_CBRI_Principals_Residence_2.pdf")
    output_dir = os.getenv("TEMP_PAGES_DIR", "temp_pages")

    if not os.path.exists(pdf_path):
        pdf_files = glob.glob("*.pdf")
        if not pdf_files:
            raise FileNotFoundError("PDF file missing in root directory.")
        pdf_path = pdf_files[0]

    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Extracting pages from: {pdf_path}")

    doc = pymupdf.open(pdf_path)
    for index, page in enumerate(doc, start=1):
        zoom = 200 / 72  # High resolution matrix
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        output_file = os.path.join(output_dir, f"page_{index}.jpeg")
        pix.save(output_file)

    print(f"[✓] Converted {len(doc)} pages into '{output_dir}/'")

if __name__ == "__main__":
    convert_pdf_to_images()