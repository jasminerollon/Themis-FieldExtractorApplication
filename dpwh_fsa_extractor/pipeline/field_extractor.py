import pandas as pd
from pathlib import Path
from dpwh_fsa_extractor.fsa import (
    fsa_contract_cost,
    fsa_contract_dates,
    fsa_contract_id,
    fsa_implementing_office,
)

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_PATH = PROJECT_ROOT / "output" / "parallel_sentences.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "output" / "extracted_fields.xlsx"

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
            
    extracted["contract_dates"] = " | ".join(extracted["contract_dates"]) if extracted["contract_dates"] else None
    
    return extracted

def main():
    print("=" * 60)
    print("Field Extractor - Running FSAs")
    print("=" * 60)
    
    if not INPUT_PATH.exists():
        print(f"Error: Input file not found at {INPUT_PATH}")
        return
        
    print(f"Reading: {INPUT_PATH}")
    df = pd.read_excel(INPUT_PATH)
    
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_excel(OUTPUT_PATH, index=False)
    
    print(f"Extracted fields saved to: {OUTPUT_PATH}")
    print(f"Total rows processed: {len(out_df)}")

if __name__ == "__main__":
    main()
