import pandas as pd
from pathlib import Path
import re
from dpwh_fsa_extractor.fsa import fsa_contract_cost, fsa_contract_dates, fsa_contract_id, fsa_implementing_office

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_FILE = BASE_DIR / "output" / "extracted_fields_2023.xlsx"
GROUND_TRUTH_FILE = BASE_DIR / "data" / "validation" / "ground_truth.csv"


def normalize(s):
    """Normalize for comparison."""
    if pd.isna(s) or s == "":
        return ""
    return " ".join(str(s).replace(',', '').split()).lower()


# Test cases: (input_id, input_cost, input_date, input_office, should_be_valid, description)
TEST_CASES = [
    # Valid cases
    ("12A3456", "96,480,700.00", "July 11, 2023", "Abra District Engineering Office", True, "Valid: standard format"),
    ("9921234", "87,814,653.82", "April 08, 2024", "North Manila District Engineering Office", True, "Valid: different values"),
    ("0BB0000", "63,351,310.49", "December 15, 2023", "Abra District Engineering Office", True, "Valid: zeros in ID"),
    ("12A34567", "94,573,295.00", "March 09, 2023", "North Manila District Engineering Office", True, "Valid: 5 digits after letter"),
    ("12AB345", "47,875,326.90", "March 28, 2023", "North Manila District Engineering Office", True, "Valid: 2 letters"),
    # Invalid cases - should be REJECTED
    ("1A123", "invalid", "2/3/2022", "RandomOffice", False, "Invalid: 1 digit before letter, wrong date format"),
    ("AB123", "abc123", "13/45/2099", "FakeOffice", False, "Invalid: no leading digits, invalid cost/date/office"),
]


def main():
    print("=" * 140)
    print("PART A: FSA VALIDATION - PREDEFINED TEST CASES (Valid & Invalid)")
    print("=" * 140)
    print()

    field_stats_fsa = {
        "Contract ID": {"total": 0, "correct": 0},
        "Contract Cost": {"total": 0, "correct": 0},
        "Contract Date": {"total": 0, "correct": 0},
        "Implementing Office": {"total": 0, "correct": 0},
    }

    print(f"{'Input ID':<12} {'Input Cost':<18} {'Input Date':<18} {'Status':<12} {'Description':<35}")
    print("-" * 140)

    for input_id, input_cost, input_date, input_office, should_be_valid, description in TEST_CASES:
        # Run FSAs
        id_result = fsa_contract_id.run_fsa(input_id)
        cost_result = fsa_contract_cost.run_fsa(input_cost)
        date_result = fsa_contract_dates.run_fsa(input_date)
        office_result = fsa_implementing_office.run_fsa(input_office)

        # For valid cases: FSA should accept (matched=True)
        # For invalid cases: FSA should reject (matched=False)
        id_correct = (id_result["matched"] == should_be_valid)
        cost_correct = (cost_result["matched"] == should_be_valid)
        date_correct = (date_result["matched"] == should_be_valid)
        office_correct = (office_result["matched"] == should_be_valid)

        id_status = "PASS (Accept)" if id_result["matched"] else "PASS (Reject)" if not should_be_valid else "FAIL"
        cost_status = "PASS (Accept)" if cost_result["matched"] else "PASS (Reject)" if not should_be_valid else "FAIL"
        date_status = "PASS (Accept)" if date_result["matched"] else "PASS (Reject)" if not should_be_valid else "FAIL"
        office_status = "PASS (Accept)" if office_result["matched"] else "PASS (Reject)" if not should_be_valid else "FAIL"

        print(f"{input_id:<12} {input_cost:<18} {input_date:<18} {id_status:<12} {description:<35}")

        field_stats_fsa["Contract ID"]["total"] += 1
        if id_correct:
            field_stats_fsa["Contract ID"]["correct"] += 1

        field_stats_fsa["Contract Cost"]["total"] += 1
        if cost_correct:
            field_stats_fsa["Contract Cost"]["correct"] += 1

        field_stats_fsa["Contract Date"]["total"] += 1
        if date_correct:
            field_stats_fsa["Contract Date"]["correct"] += 1

        field_stats_fsa["Implementing Office"]["total"] += 1
        if office_correct:
            field_stats_fsa["Implementing Office"]["correct"] += 1

        print("-" * 140)

    print()
    print("FSA Validation Results")
    print("=" * 70)
    fsa_overall_pass = 0
    for field, stats in field_stats_fsa.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        fsa_overall_pass += accuracy
        print(f"{field:<25} {stats['correct']}/{stats['total']} correct ({accuracy:.2f}%)")

    fsa_avg_accuracy = fsa_overall_pass / 4
    print(f"\n{'Overall FSA Validation':<25} {fsa_avg_accuracy:.2f}%")
    print()

    # Part B: Real extraction validation
    print("=" * 140)
    print("PART B: EXTRACTION VALIDATION AGAINST REAL DPWH DATA")
    print("=" * 140)
    print()

    try:
        extracted_df = pd.read_excel(EXTRACTED_FILE)
        ground_truth_df = pd.read_csv(GROUND_TRUTH_FILE)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # Match and validate Contract IDs
    extracted_df['match_key'] = extracted_df['contract_id'].apply(
        lambda x: re.sub(r'[^A-Z0-9]', '', str(x).upper()) if pd.notna(x) else ""
    )
    ground_truth_df['match_key'] = ground_truth_df['contract_id_gt'].apply(
        lambda x: re.sub(r'[^A-Z0-9]', '', str(x).upper()) if pd.notna(x) else ""
    )

    merged_df = pd.merge(ground_truth_df, extracted_df, on='match_key', how='left')

    total_gt = len(ground_truth_df)
    matched_count = merged_df['contract_id'].notna().sum()

    print(f"Ground Truth Records: {total_gt}")
    print(f"Successfully Extracted Contract IDs: {matched_count}")
    print(f"Extraction Success Rate: {(matched_count / total_gt * 100):.2f}%")
    print()

    # Sample validations for ALL fields
    print(f"{'GT ID':<15} {'GT Cost':<18} {'Ext Cost':<18} {'Cost':<10} {'GT Date':<18} {'Ext Date':<18} {'Date':<10} {'GT Office':<30} {'Ext Office':<30} {'Office':<10}")
    print("-" * 180)

    sample_count = 0
    id_correct = 0
    cost_correct = 0
    date_correct = 0
    office_correct = 0

    for idx, row in merged_df.iterrows():
        if pd.isna(row['contract_id']):
            continue

        gt_id = row.get('contract_id_gt', "")
        ext_id = row.get('contract_id', "")
        gt_cost = row.get('contract_cost_gt', "")
        ext_cost = row.get('contract_cost', "")
        gt_date = row.get('contract_date_gt', "")
        ext_date = row.get('contract_dates', "")
        # Extract only the FIRST date (effectivity date, not expiry date)
        if ext_date and '|' in str(ext_date):
            ext_date = str(ext_date).split('|')[0].strip()
        gt_office = row.get('implementing_office_gt', "")
        ext_office = row.get('implementing_office', "")

        id_match = normalize(str(gt_id)) == normalize(str(ext_id))
        cost_match = normalize(str(gt_cost)) == normalize(str(ext_cost))
        date_match = normalize(str(gt_date)) == normalize(str(ext_date))
        office_match = normalize(str(gt_office)) == normalize(str(ext_office))

        if id_match:
            id_correct += 1
        if cost_match:
            cost_correct += 1
        if date_match:
            date_correct += 1
        if office_match:
            office_correct += 1

        if sample_count < 5:
            id_status = "MATCH" if id_match else "MISMATCH"
            cost_status = "MATCH" if cost_match else "MISMATCH"
            date_status = "MATCH" if date_match else "MISMATCH"
            office_status = "MATCH" if office_match else "MISMATCH"

            print(f"{str(gt_id):<15} {str(gt_cost):<18} {str(ext_cost):<18} {cost_status:<10} {str(gt_date):<18} {str(ext_date):<18} {date_status:<10} {str(gt_office):<30} {str(ext_office):<30} {office_status:<10}")
            sample_count += 1

    print()
    print("=" * 180)
    print("Field Extraction Accuracy")
    print("=" * 180)
    matched_count = id_correct

    print(f"Contract ID      | Total: {matched_count:<3} | Correct: {id_correct:<3} | Accuracy: {(id_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract ID      | No matches")
    print(f"Contract Cost    | Total: {matched_count:<3} | Correct: {cost_correct:<3} | Accuracy: {(cost_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract Cost    | No matches")
    print(f"Contract Date    | Total: {matched_count:<3} | Correct: {date_correct:<3} | Accuracy: {(date_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract Date    | No matches")
    print(f"Implementing Off | Total: {matched_count:<3} | Correct: {office_correct:<3} | Accuracy: {(office_correct/matched_count*100):.2f}%" if matched_count > 0 else "Implementing Off | No matches")

    print()
    print("=" * 180)
    print("VALIDATION SUMMARY")
    print("=" * 180)
    print(f"FSA Validation (Test Cases):                {fsa_avg_accuracy:.2f}% - Correct acceptance/rejection")
    print(f"Real Data Extraction Success:               {(matched_count/total_gt*100):.2f}% - Extraction from DPWH PDFs")
    print(f"Contract ID Accuracy:                       {(id_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract ID Accuracy:                       N/A")
    print(f"Contract Cost Accuracy:                     {(cost_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract Cost Accuracy:                     N/A")
    print(f"Contract Date Accuracy:                     {(date_correct/matched_count*100):.2f}%" if matched_count > 0 else "Contract Date Accuracy:                     N/A")
    print(f"Implementing Office Accuracy:               {(office_correct/matched_count*100):.2f}%" if matched_count > 0 else "Implementing Office Accuracy:               N/A")
    print("=" * 180)


if __name__ == "__main__":
    main()
