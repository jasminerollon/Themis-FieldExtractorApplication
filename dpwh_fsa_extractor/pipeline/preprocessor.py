import re
import pandas as pd
from pathlib import Path
from typing import Dict, List

# Path Config
EXTRACTED_DIR = Path(__file__).parent.parent / "data" / "extracted"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "parallel_sentences.xlsx"

def clean_string(text) -> str:
    """
    Stage 1: Encoding and Character Normalization
    Removes invalid Excel/XML characters. Strips out characters that
    excel cannot render or characters that would break XML parsing in
    .xlsx files
    :param text: Raw string from PDF extraction
    :return: Cleaned string with only valid Excel characters
    """
    if text is None or text == 'nan':
        return ""

    text = str(text)
    text = ''.join(c for c in text if ord(c) < 0xFFFE)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text.strip()

def is_valid_row(row: str) -> bool:
    """
    Stage 2: Noise Filtering
    Check if a table row has meaningful content. It filters out
    separator lines, table markers, and empty rows.
    :param row: A single line from the extracted text file, representing one row
    :return: True if the row has meaningful content; False if the row only contains noise
    """
    if not row or not row.strip():
        return False

    if re.match(r'^[|\-\s]+$', row):
        return False

    if re.match(r'^TABLE\s+\d+', row, re.IGNORECASE):
        return False

    cells = [c.strip() for c in row.split('|') if c.strip()]

    if len(cells) == 0:
        return False

    if not any(c.isalnum() for cell in cells for c in cell):
        return False

    return True

def normalize_whitespace(text: str) -> str:
    """
    Stage 3: Structural Cleaning
    Cleans up whitespace and compress multiple empty pipes
    :param text: Raw strings from PDF extraction which contains irregular formatting
    :return: String with normalized whitespace and standardized pipe formatting
    """
    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'\|\s*\|\s*\|', '| | |', text)
    text = re.sub(r'\|\s*\|', '| |', text)

    text = re.sub(r'\s*\|\s*', ' | ', text)

    text = re.sub(r'^\|\s+', '', text)
    text = re.sub(r'\s+\|$', '', text)

    return text.strip()

def expand_abbreviations(text: str) -> str:
    """
    Stage 4.1: Linguistic Normalization
    Expands common DPWH abbreviations to their full, human-readable forms.
    It standardizes abbreviated terms that appear frequently in DPWH regional reports.
    :param text: String containing DPWH abbreviations that can be expanded
    :return: String with all recognized abbreviations expanded to their full forms.
    """
    abbr = {
        r'\bDPWH\b': 'Department of Public Works and Highways',
        r'\bMOOE\b': 'Maintenance and Other Operating Expenses',
        r'\bPS\b': 'Personal Services',
        r'\bCO\b': 'Capital Outlay',
        r'\bNCR\b': 'National Capital Region',
        r'\bSPF\b': 'Special Purpose Fund',
        r'\bQRF\b': 'Quick Response Fund',
        r'\bNDRRMF\b': 'National Disaster Risk Reduction and Management Fund',
        r'\bUPMO\b': 'Unified Project Management Office',
        r'\bOSEC\b': 'Office of the Secretary',
        r'\bFY\b': 'Fiscal Year',
    }

    for pat, repl in abbr.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)

    return text

def normalize_currency(text: str) -> str:
    """
    Stage 4.2: Linguistic Normalization
    Strips peso symbols and currency prefixes while preserving comma-grouped
    decimal amounts required by grammar G2 / fsa_contract_cost.
    """
    text = re.sub(r'[₱\u20b1]\s*', '', text)
    text = re.sub(r'\bPhP\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPHP\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

def normalize_cell(cell: str) -> str:
    """
    Stage 4.3: Linguistic Normalization
    Normalizes individual cell content. Applies abbreviation expansion,
    currency normalization, and whitespace cleaning.
    :param cell: Unformatted cell string
    :return: Formatted cell string
    """
    if not cell or not cell.strip():
        return ""

    cell = cell.strip()

    if cell == '' or cell == ' ':
        return ""

    cell = expand_abbreviations(cell)
    cell = normalize_currency(cell)
    cell = normalize_whitespace(cell)

    return cell.strip()

def normalize_full_row(row: str) -> str:
    """
    Stage 5.1: Segmentation and Row Processing
    Normalizes a full table row which handles sparse columns. Splits cells
    by pipe, normalizes each cell that was separated, rejoins the normalized
    separated cells.
    :param row: A raw table row string from PDF extraction
    :return: Normalized row string with cleaned cells and standardized pipe formatting
    """
    if not row.strip():
        return ""

    cells = row.split('|')

    normalized_cells = []
    for cell in cells:
        norm_cell = normalize_cell(cell)
        normalized_cells.append(norm_cell if norm_cell else "")

    while normalized_cells and not normalized_cells[-1]:
        normalized_cells.pop()

    if not any(c for c in normalized_cells if c):
        return ""

    return ' | '.join(normalized_cells)

def process_table_file(raw_text: str, region: str) -> List[Dict[str, str]]:
    """
    Stage 5.2: Segmentation and Row Processing
    Processes extracted table file with sparse columns.
    :param raw_text: Raw extracted text from PDF
    :param region: Region name
    :return: List of sentence dicts with region, raw, normalized
    """
    if not raw_text:
        return []

    results = []
    lines = raw_text.split('\n')

    for line in lines:
        line = line.strip()

        if not is_valid_row(line):
            continue

        raw_row = clean_string(line)
        normalized_row = normalize_full_row(line)
        normalized_row = clean_string(normalized_row)

        if not normalized_row:
            continue

        results.append({
            "raw": raw_row,
            "normalized": normalized_row,
            "region": region
        })

    return results


def extract_region_from_filename(filename: str) -> str:
    """
    Helper function that extracts the region name from the PDF filename
    :param filename: The filename of the PDF containing region names
    :return: The region name from the filename of the PDF
    """
    match = re.search(r'DPWH-([A-Z0-9]+)-INFRA', filename)

    if not match:
        return "Unknown"

    region_code = match.group(1)

    region_map = {
        'NCR': 'National Capital Region',
        'NIR': 'Negros Island Region',
        'BENGUET': 'Benguet',
        'CENTRALOFFICE': 'Central Office',
        'MIMAROPA': 'MIMAROPA',
        'REGIONI': 'Region I - Ilocos Region',
        'REGIONII': 'Region II - Cagayan Valley',
        'REGIONIII': 'Region III - Central Luzon',
        'REGIONIVA': 'Region IV-A - CALABARZON',
        'REGIONV': 'Region V - Bicol Region',
        'REGIONVI': 'Region VI - Western Visayas',
        'REGIONVII': 'Region VII - Central Visayas',
        'REGIONVIII': 'Region VIII - Eastern Visayas',
        'REGIONIX': 'Region IX - Zamboanga Peninsula',
        'REGIONX': 'Region X - Northern Mindanao',
        'REGIONXI': 'Region XI - Davao Region',
        'REGIONXII': 'Region XII - SOCCSKSARGEN',
        'REGIONXIII': 'Region XIII - Caraga',
    }

    return region_map.get(region_code, f"Unknown ({region_code})")

def generate_parallel_sentences_excel():
    """
    Process all extracted .txt files and generates a parallel_sentences.xlsx
    :return: The generated .xlsx file
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_sentences = []
    txt_files = list(EXTRACTED_DIR.glob("*.txt"))

    if not txt_files:
        print(f"Error: No .txt files found in {EXTRACTED_DIR}")
        return None

    print("-" * 50)
    print("PREPROCESSING & EXCEL GENERATION")
    print("-" * 50)

    for txt_path in txt_files:
        filename = txt_path.name.replace(".txt", ".pdf")
        region = extract_region_from_filename(filename)

        print(f"\n Processing: {filename}")
        print(f"   Region: {region}")

        with open(txt_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        print(f"   File size: {len(raw_text):,} characters")

        sentences = process_table_file(raw_text, region)

        print(f"   Generated {len(sentences):,} valid sentences")
        all_sentences.extend(sentences)

    data = []
    for s in all_sentences:
        data.append({
            'region': s['region'],
            'raw_sentence': s['raw'],
            'normalized_sentence': s['normalized']
        })

    if not data:
        print("\n No valid data to save")
        return None

    df = pd.DataFrame(data)

    try:
        df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
        print(f"\n Saved to: {OUTPUT_FILE}")
        print(f"   Total rows: {len(df):,}")
    except Exception as e:
        print(f"\n Error: {e}")
        csv_file = OUTPUT_DIR / "parallel_sentences.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"   Saved as CSV: {csv_file}")

    return df

if __name__ == "__main__":
    generate_parallel_sentences_excel()