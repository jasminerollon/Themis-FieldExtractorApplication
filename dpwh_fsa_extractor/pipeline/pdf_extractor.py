import pdfplumber
import os
from pathlib import Path

# Path Config
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_PDF_DIR_2024 = DATA_DIR / "raw"
RAW_PDF_DIR_2023 = DATA_DIR / "validation" / "2023"
EXTRACTED_DIR_2024 = DATA_DIR / "extracted" / "2024"
EXTRACTED_DIR_2023 = DATA_DIR / "extracted" / "2023"

PDF_FILES_2023 = [
    "DPWH-CAR-INFRA.pdf",
    "DPWH-NCR-INFRA.pdf",
    "DPWH-REGIONIII-INFRA.pdf",
]

PDF_FILES = [
    "DPWH-CAR-INFRA.pdf",
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


def save_extracted_text(pdf_name, extracted_text, output_dir):
    """
    This function saves extracted text to a .txt file
    :param pdf_name: (str) Original PDF filename that will be converted to .txt
    :param extracted_text: (str) Extracted text content
    :param output_dir: (Path) Output directory
    """
    initial_name = pdf_name.replace(".pdf", ".txt")
    output_path = os.path.join(output_dir, initial_name)
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(extracted_text)
    print(f"Saved extracted text to {output_path}")


def process_corpus(corpus_year, raw_dir, extracted_dir, pdf_files=None):
    if pdf_files is None:
        pdf_files = PDF_FILES

    print(f"\nProcessing {corpus_year} Corpus")
    print("-" * 50)
    success_count = 0
    fail_count = 0

    extracted_dir.mkdir(parents=True, exist_ok=True)

    for pdf_file in pdf_files:  # <-- uses the passed-in list now
        pdf_path = os.path.join(raw_dir, pdf_file)
        print(f"\n Processing: {pdf_file}")
        if not os.path.exists(pdf_path):
            print(f"Error: File not found at {pdf_path}")
            fail_count += 1
            continue
        extracted_text = extract_pdf_text(pdf_path)
        save_extracted_text(pdf_file, extracted_text, extracted_dir)
        success_count += 1

    print("\n" + "-" * 50)
    print(f"{corpus_year} EXTRACTION COMPLETE")
    print("-" * 50)
    print(f"Successful: {success_count} out of {len(pdf_files)}")
    print(f"Failed: {fail_count} out of {len(pdf_files)}")
    print(f"Output directory: {extracted_dir}")
    print("-" * 50)

def main():
    print("-" * 50)
    print("PDF TEXT EXTRACTOR")
    print("-" * 50)

    # Process 2024 (Primary Corpus) — all 18 regions
    process_corpus("2024", RAW_PDF_DIR_2024, EXTRACTED_DIR_2024)

    # Process 2023 (Validation Corpus) — only 3 regions
    process_corpus("2023", RAW_PDF_DIR_2023, EXTRACTED_DIR_2023, PDF_FILES_2023)

if __name__ == "__main__":
    main()