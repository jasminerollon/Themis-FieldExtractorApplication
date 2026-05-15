import pandas as pd
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
EXTRACTED_PATH = PROJECT_ROOT / "output" / "extracted_fields.xlsx"
CSV_PATH = PROJECT_ROOT / "data" / "validation" / "dpwh_transparency_data.csv"
REPORT_PATH = PROJECT_ROOT / "output" / "validation_report.xlsx"

def parse_fsa_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y").date()
    except ValueError:
        return None

def parse_csv_date(date_str):
    if pd.isna(date_str) or not str(date_str).strip():
        return None
    try:
        return datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None

def normalize_cost(cost_str):
    if pd.isna(cost_str) or not str(cost_str).strip():
        return None
    try:
        return float(str(cost_str).replace(',', ''))
    except ValueError:
        return None

def normalize_office(office_str):
    if pd.isna(office_str):
        return ""
    s = str(office_str).lower()
    s = s.replace("district engineering office", "deo")
    return s.strip()

def main():
    print("=" * 60)
    print("Metrics & Validation Report")
    print("=" * 60)

    if not EXTRACTED_PATH.exists():
        print(f"Error: {EXTRACTED_PATH} not found. Please run field_extractor.py first.")
        return
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    print("Loading data...")
    ext_df = pd.read_excel(EXTRACTED_PATH)
    
    # Load CSV in chunks or only relevant columns to save memory
    csv_df = pd.read_csv(CSV_PATH, usecols=["contractId", "budget", "startDate", "completionDate", "location"], dtype=str)
    
    # Create lookup dict for faster matching
    csv_dict = csv_df.set_index("contractId").to_dict("index")

    report_rows = []
    
    metrics = {
        "contract_id": {"processed": 0, "valid": 0, "rejected": 0, "tp": 0, "fp": 0, "fn": 0},
        "contract_cost": {"processed": 0, "valid": 0, "rejected": 0, "tp": 0, "fp": 0, "fn": 0},
        "contract_dates": {"processed": 0, "valid": 0, "rejected": 0, "tp": 0, "fp": 0, "fn": 0},
        "implementing_office": {"processed": 0, "valid": 0, "rejected": 0, "tp": 0, "fp": 0, "fn": 0},
    }
    
    total_rows = len(ext_df)
    matched_contracts = 0

    for _, row in ext_df.iterrows():
        # Process general metrics (Validation Coverage, Success Rate, etc.)
        for field in ["contract_id", "contract_cost", "contract_dates", "implementing_office"]:
            metrics[field]["processed"] += 1
            ext_val = row.get(field)
            if not pd.isna(ext_val) and bool(str(ext_val).strip()):
                metrics[field]["valid"] += 1
            else:
                metrics[field]["rejected"] += 1

        c_id = row.get("contract_id")
        cost = row.get("contract_cost")
        dates = row.get("contract_dates")
        office = row.get("implementing_office")
        
        has_id = not pd.isna(c_id) and bool(str(c_id).strip())

        report_row = {
            "contract_id": c_id,
            "raw_sentence": row.get("raw_sentence"),
            "extracted_cost": cost,
            "csv_budget": None,
            "cost_match": False,
            "extracted_dates": dates,
            "csv_start_date": None,
            "csv_completion_date": None,
            "date_match": False,
            "extracted_office": office,
            "csv_location": None,
            "office_match": False
        }

        # Evaluate TP, FP, FN
        if has_id:
            if c_id in csv_dict:
                metrics["contract_id"]["tp"] += 1
                matched_contracts += 1
                csv_data = csv_dict[c_id]
                
                # --- Cost Match ---
                report_row["csv_budget"] = csv_data.get("budget")
                has_cost = not pd.isna(cost) and bool(str(cost).strip())
                gt_cost = csv_data.get("budget")
                has_gt_cost = not pd.isna(gt_cost) and bool(str(gt_cost).strip())
                
                match_cost = False
                if has_cost and has_gt_cost:
                    ex_cost = normalize_cost(cost)
                    csv_cost = normalize_cost(gt_cost)
                    if ex_cost is not None and csv_cost is not None and abs(ex_cost - csv_cost) < 1.0:
                        match_cost = True
                        
                if match_cost:
                    report_row["cost_match"] = True
                    metrics["contract_cost"]["tp"] += 1
                else:
                    if has_cost: metrics["contract_cost"]["fp"] += 1
                    if has_gt_cost: metrics["contract_cost"]["fn"] += 1
            
                # --- Date Match ---
                report_row["csv_start_date"] = csv_data.get("startDate")
                report_row["csv_completion_date"] = csv_data.get("completionDate")
                has_dates = not pd.isna(dates) and bool(str(dates).strip())
                gt_start = csv_data.get("startDate")
                gt_end = csv_data.get("completionDate")
                has_gt_dates = (not pd.isna(gt_start) and bool(str(gt_start).strip())) or \
                               (not pd.isna(gt_end) and bool(str(gt_end).strip()))
                
                match_date = False
                if has_dates:
                    ex_dates = [d.strip() for d in str(dates).split('|') if d.strip()]
                    csv_start = parse_csv_date(gt_start)
                    csv_end = parse_csv_date(gt_end)
                    
                    for d in ex_dates:
                        parsed_d = parse_fsa_date(d)
                        if parsed_d and (parsed_d == csv_start or parsed_d == csv_end):
                            match_date = True
                            break
                            
                if match_date:
                    report_row["date_match"] = True
                    metrics["contract_dates"]["tp"] += 1
                else:
                    if has_dates: metrics["contract_dates"]["fp"] += 1
                    if has_gt_dates: metrics["contract_dates"]["fn"] += 1
                    
                # --- Office Match ---
                report_row["csv_location"] = csv_data.get("location")
                has_office = not pd.isna(office) and bool(str(office).strip())
                gt_loc = csv_data.get("location")
                has_gt_office = False
                match_office = False
                
                if not pd.isna(gt_loc):
                    try:
                        loc_dict = json.loads(str(gt_loc))
                        prov = normalize_office(loc_dict.get("province", ""))
                        reg = normalize_office(loc_dict.get("region", ""))
                        if prov or reg:
                            has_gt_office = True
                            if has_office:
                                ex_off = normalize_office(office)
                                if (ex_off and (ex_off in prov or ex_off in reg or prov in ex_off or reg in ex_off)):
                                    match_office = True
                    except json.JSONDecodeError:
                        pass
                        
                if match_office:
                    report_row["office_match"] = True
                    metrics["implementing_office"]["tp"] += 1
                else:
                    if has_office: metrics["implementing_office"]["fp"] += 1
                    if has_gt_office: metrics["implementing_office"]["fn"] += 1

            else:
                # Extracted ID not in CSV -> False Positive for ID
                metrics["contract_id"]["fp"] += 1
        else:
            # No ID extracted -> False Negative for ID
            metrics["contract_id"]["fn"] += 1

        report_rows.append(report_row)

    report_df = pd.DataFrame(report_rows)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report_df.to_excel(REPORT_PATH, index=False)
    print(f"Validation report saved to {REPORT_PATH}")

    print("\n--- Metrics ---")
    print(f"Total rows processed: {total_rows}")
    print(f"Contracts matched in CSV: {matched_contracts}")
    
    for field, data in metrics.items():
        processed = data["processed"]
        expected = processed  # Based on Validation Coverage formula
        valid = data["valid"]
        rejected = data["rejected"]
        tp = data["tp"]
        fp = data["fp"]
        fn = data["fn"]
        
        validation_coverage = (processed / expected) * 100 if expected > 0 else 0
        extraction_success_rate = (valid / processed) * 100 if processed > 0 else 0
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        recognized_valid_string_count = valid
        invalid_string_detection_rate = (rejected / processed) * 100 if processed > 0 else 0
        overall_data_quality = (valid / processed) * 100 if processed > 0 else 0
        
        print(f"\nField: {field}")
        print(f"  Validation Coverage:             {validation_coverage:.2f}% ({processed}/{expected})")
        print(f"  Extraction Success Rate:         {extraction_success_rate:.2f}% ({valid}/{processed})")
        print(f"  Precision:                       {precision:.2f}% ({tp}/{tp+fp})")
        print(f"  Recall:                          {recall:.2f}% ({tp}/{tp+fn})")
        print(f"  F1-Score:                        {f1_score:.2f}%")
        print(f"  Recognized Valid String Count:   {recognized_valid_string_count}")
        print(f"  Invalid String Detection Rate:   {invalid_string_detection_rate:.2f}% ({rejected}/{processed})")
        print(f"  Overall Data Quality Assessment: {overall_data_quality:.2f}% ({valid}/{processed})")

if __name__ == "__main__":
    main()
