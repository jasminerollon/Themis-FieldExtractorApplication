import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXTRACTED_PATH = PROJECT_ROOT / "output" / "extracted_fields_2023.xlsx"
CSV_PATH = PROJECT_ROOT / "data" / "validation" / "ground_truth.csv"
REPORT_PATH = PROJECT_ROOT / "output" / "validation_report.xlsx"

def normalize_string(s):
    if pd.isna(s) or s is None:
        return ""
    return str(s).strip()

def normalize_cost(s):
    if pd.isna(s) or s is None:
        return ""
    # Remove commas and spaces for numeric comparison, or just string compare
    # Let's keep it as string without commas and spaces for robust comparison
    s = str(s).replace(',', '').strip()
    try:
        # if it can be a float, format it to 2 decimal places string
        return f"{float(s):.2f}"
    except ValueError:
        return s

def main():
    print("=" * 60)
    print("Metrics & Validation Report (2023 Ground Truth)")
    print("=" * 60)

    if not EXTRACTED_PATH.exists():
        print(f"Error: {EXTRACTED_PATH} not found. Please run field_extractor.py first.")
        return
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found. Please create the ground truth CSV.")
        return

    print("Loading data...")
    ext_df = pd.read_excel(EXTRACTED_PATH)
    gt_df = pd.read_csv(CSV_PATH)

    report_rows = []
    
    metrics = {
        "contract_id": {"tp": 0, "fp": 0, "fn": 0},
        "contract_cost": {"tp": 0, "fp": 0, "fn": 0},
        "contract_date": {"tp": 0, "fp": 0, "fn": 0},
        "implementing_office": {"tp": 0, "fp": 0, "fn": 0},
    }

    # Map the FSA extracted column names to our standard fields
    fsa_col_map = {
        "contract_id": "contract_id",
        "contract_cost": "contract_cost",
        "contract_date": "contract_dates", # note the plural in extracted fields
        "implementing_office": "implementing_office"
    }

    matched_records = 0
    unmatched_records = 0

    for _, gt_row in gt_df.iterrows():
        gt_region = normalize_string(gt_row.get("region"))
        gt_id = normalize_string(gt_row.get("contract_id_gt"))
        
        if not gt_id:
            continue

        # Find matching row in extracted data
        # We match on region and the raw_sentence containing the ground truth contract ID
        # because the PDF row will contain the contract ID.
        mask = (ext_df["region"].astype(str).str.strip() == gt_region) & \
               (ext_df["raw_sentence"].astype(str).str.contains(gt_id, regex=False, na=False))
        
        matches = ext_df[mask]
        
        if len(matches) == 0:
            unmatched_records += 1
            fsa_row = None
            print(f"Warning: Could not find extracted row for GT Contract ID: {gt_id} in Region: {gt_region}")
        else:
            matched_records += 1
            fsa_row = matches.iloc[0]

        report_row = {
            "record_id": gt_row.get("record_id"),
            "region": gt_region,
            "raw_sentence": fsa_row["raw_sentence"] if fsa_row is not None else ""
        }

        # Evaluate each field
        for field in ["contract_id", "contract_cost", "contract_date", "implementing_office"]:
            gt_val = normalize_string(gt_row.get(f"{field}_gt"))
            
            fsa_col = fsa_col_map[field]
            fsa_val = normalize_string(fsa_row[fsa_col]) if fsa_row is not None else ""
            
            report_row[f"{field}_ground_truth"] = gt_val
            report_row[f"{field}_extracted"] = fsa_val
            
            if not gt_val:
                # If ground truth is empty, skip evaluation for this field (not in PDF)
                report_row[f"{field}_match"] = "N/A (No GT)"
                continue
                
            # Normalization for comparison
            if field == "contract_cost":
                comp_gt = normalize_cost(gt_val)
                comp_fsa = normalize_cost(fsa_val)
            else:
                comp_gt = gt_val.lower()
                comp_fsa = fsa_val.lower()
                
            is_match = (comp_fsa == comp_gt) if comp_fsa else False
            
            # For dates, it might extract multiple dates or slightly different formats.
            # We do a basic substring match if exact match fails for dates and offices.
            if not is_match and comp_fsa and field in ["contract_date", "implementing_office"]:
                if comp_gt in comp_fsa or comp_fsa in comp_gt:
                    is_match = True

            report_row[f"{field}_match"] = is_match

            if is_match:
                metrics[field]["tp"] += 1
            elif fsa_val:
                metrics[field]["fp"] += 1
            else:
                metrics[field]["fn"] += 1

        report_rows.append(report_row)

    report_df = pd.DataFrame(report_rows)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_excel(REPORT_PATH, index=False)
    print(f"Validation report saved to {REPORT_PATH}")

    # --- Aggregate counts for additional metrics ---
    total_gt_records = len([r for r in report_rows])
    total_expected_fields = total_gt_records * 4  # 4 fields per record

    # Count fields that had a non-empty extracted value (processed by FSA)
    fields_successfully_processed = 0
    fields_with_valid_extraction = 0
    fields_rejected = 0

    for row in report_rows:
        for field in ["contract_id", "contract_cost", "contract_date", "implementing_office"]:
            gt_val = row.get(f"{field}_ground_truth", "")
            fsa_val = row.get(f"{field}_extracted", "")
            match_val = row.get(f"{field}_match", "N/A (No GT)")

            if match_val == "N/A (No GT)":
                continue  # skip fields with no ground truth

            fields_successfully_processed += 1
            if fsa_val:
                fields_with_valid_extraction += 1
            else:
                fields_rejected += 1

    validation_coverage = (
                fields_successfully_processed / total_expected_fields * 100) if total_expected_fields > 0 else 0
    extraction_success_rate = (
                fields_with_valid_extraction / fields_successfully_processed * 100) if fields_successfully_processed > 0 else 0
    invalid_detection_rate = (
                fields_rejected / fields_successfully_processed * 100) if fields_successfully_processed > 0 else 0
    overall_quality = extraction_success_rate  # same formula per Table 7

    print("\n--- Metrics ---")
    print(f"Total Ground Truth Records:                    {len(gt_df)}")
    print(f"Records successfully matched with extraction:  {matched_records}")
    print(f"Records failed to match with extraction:       {unmatched_records}")

    print(f"\n--- Summary Metrics (Table 7) ---")
    print(f"  Validation Coverage:           {validation_coverage:.2f}%")
    print(f"  Extraction Success Rate:       {extraction_success_rate:.2f}%")
    print(f"  Recognized Valid String Count: {fields_with_valid_extraction}")
    print(f"  Invalid String Detection Rate: {invalid_detection_rate:.2f}%")
    print(f"  Overall Data Quality Score:    {overall_quality:.2f}%")

    for field, data in metrics.items():
        tp = data["tp"]
        fp = data["fp"]
        fn = data["fn"]

        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        print(f"\nField: {field}")
        print(f"  True Positives (TP):  {tp}")
        print(f"  False Positives (FP): {fp}")
        print(f"  False Negatives (FN): {fn}")
        print(f"  Precision:            {precision:.2f}%")
        print(f"  Recall:               {recall:.2f}%")
        print(f"  F1-Score:             {f1_score:.2f}%")

if __name__ == "__main__":
    main()