import pdfplumber
import os
from pathlib import Path

# Path Config
RAW_PDF_DIR = str(Path(__file__).parent.parent / "data" / "raw")
EXTRACTED_DIR = str(Path(__file__).parent.parent / "data" / "extracted")

PDF_FILES = [
    "COA-DPWH2024.pdf",
    "DPWH-BENGUET-INFRA.pdf",
    "DPWH-CENTRALOFFICE-INFRA.pdf",
    "DPWH-MIMAROPA-INFRA.pdf",
    "DPWH-NCR-INFRA.pdf",
    "DPWH-NIR-INFRA.pdf",
    "DPWH-REGIONI-INFRA.pdf",
    "DPWH-REGIONII-INFRA.pdf",
    "DPWH-REGIONIII-INFRA.pdf",
    "DPWH-REGIONIVA-INFRA.pdf",
    "DPWH-REGIONIX-INFRA.pdf",
    "DPWH-REGIONV-INFRA.pdf",
    "DPWH-REGIONVI-INFRA.pdf",
    "DPWH-REGIONVII-INFRA.pdf",
    "DPWH-REGIONVIII-INFRA.pdf",
    "DPWH-REGIONX-INFRA.pdf",
    "DPWH-REGIONXI-INFRA.pdf",
    "DPWH-REGIONXII-INFRA.pdf",
    "DPWH-REGIONXIII-INFRA.pdf",
]

def extract_pdf_text(pdf_path):
    """
    This function extracts texts inside tables from a PDF file using pdfplumber
    :param pdf_path: (str) Path to the PDF file
    :return: (str) Extracted text from all pages
    """
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() # Extract tables
            for table in tables:
                for row in table:
                    if row and any(cell for cell in row if cell):
                        full_text.append(" | ".join([str(cell) if cell else "" for cell in row]))
    return "\n".join(full_text)


def save_extracted_text(pdf_name, extracted_text):
    """
    This function saves extracted text to a .txt file
    :param pdf_name: (str) Original PDF filename that will be converted to .txt
    :param extracted_text: (str) Extracted text content
    """
    initial_name = pdf_name.replace(".pdf", ".txt")
    output_path = os.path.join(EXTRACTED_DIR, initial_name)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(extracted_text)
    print(f"Saved extracted text to {output_path}")

def main():
    """
    This function is the main extraction process for all PDF files
    """
    print("-" * 50)
    print("PDF TEXT EXTRACTOR")
    print("-" * 50)
    # Tracker for extraction results
    success_count = 0
    fail_count = 0
    for pdf_file in PDF_FILES:
        pdf_path = os.path.join(RAW_PDF_DIR, pdf_file)
        print(f"\n Processing: {pdf_file}")
        if not os.path.exists(pdf_path): # Checks if PDF exists
            print(f"Error: File not found at {pdf_path}")
            fail_count += 1
            continue
        extracted_text = extract_pdf_text(pdf_path) # Extract text
        save_extracted_text(pdf_file, extracted_text) # Save extracted text
        success_count += 1

    print("\n" + "-" * 50)
    print("EXTRACTION COMPLETE")
    print("-" * 50)
    print(f"Successful: {success_count} out of {len(PDF_FILES)}")
    print(f"Failed: {fail_count} out of {len(PDF_FILES)}")
    print(f"Output directory: {EXTRACTED_DIR}")
    print("-" * 50)

if __name__ == "__main__":
    main()