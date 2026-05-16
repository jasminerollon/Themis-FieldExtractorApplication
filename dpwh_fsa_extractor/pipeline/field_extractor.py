import pandas as pd
from pathlib import Path
import re
from dpwh_fsa_extractor.fsa import (
    fsa_contract_cost,
    fsa_contract_dates,
    fsa_contract_id,
    fsa_implementing_office,
)

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

def extract_fields_from_sentence(sentence_dict: dict) -> dict:
    """
    Runs all 4 FSAs on each corpus sentence (which is a table row with cells separated by |),
    and collects field values.
    """
    normalized_sentence = sentence_dict.get("normalized", "")

    extracted = {
        "region": sentence_dict.get("region", ""),
        "raw_sentence": sentence_dict.get("raw", ""),
        "contract_id": None,
        "contract_cost": None,
        "contract_dates": [],
        "implementing_office": None
    }

    if not normalized_sentence or not isinstance(normalized_sentence, str):
        extracted["contract_dates"] = None
        return extracted

    cells = [cell.strip() for cell in normalized_sentence.split("|") if cell.strip()]

    # Try individual cells first
    for cell in cells:
        id_res = fsa_contract_id.run_fsa(cell)
        if id_res.get("matched"):
            extracted["contract_id"] = id_res["value"]

        cost_res = fsa_contract_cost.run_fsa(cell)
        if cost_res.get("matched"):
            extracted["contract_cost"] = cost_res["value"]

        date_res = fsa_contract_dates.run_fsa(cell)
        if date_res.get("matched"):
            extracted["contract_dates"].append(date_res["value"])

        office_res = fsa_implementing_office.run_fsa(cell)
        if office_res.get("matched"):
            extracted["implementing_office"] = office_res["value"]

    # Try combining adjacent cells for split dates (e.g., "February 19," + "2024")
    for i in range(len(cells) - 1):
        combined = cells[i].strip() + " " + cells[i + 1].strip()
        date_res = fsa_contract_dates.run_fsa(combined)
        if date_res.get("matched") and date_res["value"] not in extracted["contract_dates"]:
            extracted["contract_dates"].append(date_res["value"])

    # Try combining multiple cells for costs (in case they're split)
    for i in range(len(cells) - 1):
        combined = cells[i].strip() + cells[i + 1].strip()
        cost_res = fsa_contract_cost.run_fsa(combined)
        if cost_res.get("matched") and not extracted["contract_cost"]:
            extracted["contract_cost"] = cost_res["value"]

    # Try entire sentence as fallback for office and cost
    full_sentence = " ".join(cells)

    if not extracted["contract_cost"]:
        # Extract all numbers that look like currency (e.g., 4,706,352.51)
        currency_pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        matches = re.findall(currency_pattern, full_sentence)
        for match in matches:
            cost_res = fsa_contract_cost.run_fsa(match)
            if cost_res.get("matched"):
                extracted["contract_cost"] = match
                break

    if not extracted["implementing_office"]:
        office_res = fsa_implementing_office.run_fsa(full_sentence)
        if office_res.get("matched"):
            extracted["implementing_office"] = office_res["value"]

    extracted["contract_dates"] = " | ".join(extracted["contract_dates"]) if extracted["contract_dates"] else None

    return extracted

def process_corpus_fields(corpus_year: str):
    input_path = OUTPUT_DIR / f"parallel_sentences_{corpus_year}.xlsx"
    output_path = OUTPUT_DIR / f"extracted_fields_{corpus_year}.xlsx"

    print(f"\nProcessing {corpus_year} corpus...")

    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        return

    print(f"Reading: {input_path}")
    df = pd.read_excel(input_path)

    results = []
    for _, row in df.iterrows():
        sentence_dict = {
            "raw": row.get("raw_sentence", ""),
            "normalized": row.get("normalized_sentence", ""),
            "region": row.get("region", "")
        }
        extracted = extract_fields_from_sentence(sentence_dict)
        results.append(extracted)

    out_df = pd.DataFrame(results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_excel(output_path, index=False)

    print(f"Extracted fields saved to: {output_path}")
    print(f"Total rows processed: {len(out_df)}")

def main():
    print("=" * 60)
    print("Field Extractor - Running FSAs")
    print("=" * 60)

    process_corpus_fields("2024")
    process_corpus_fields("2023")

if __name__ == "__main__":
    main()
