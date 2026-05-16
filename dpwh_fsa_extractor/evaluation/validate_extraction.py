import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_FILE = BASE_DIR / "output" / "extracted_fields_2023.xlsx"
GROUND_TRUTH_FILE = BASE_DIR / "data" / "validation" / "ground_truth.csv"
OUTPUT_FILE = BASE_DIR / "output" / "validation_results.xlsx"


def normalize(s):
    """Normalize for comparison."""
    if pd.isna(s) or s == "":
        return ""
    return " ".join(str(s).replace(',', '').split()).lower()


def main():
    print("=" * 100)
    print("VALIDATION RESULTS GENERATOR")
    print("=" * 100)

    try:
        extracted_df = pd.read_excel(EXTRACTED_FILE)
        ground_truth_df = pd.read_csv(GROUND_TRUTH_FILE)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    print(f"\nLoaded {len(extracted_df)} extracted records")
    print(f"Loaded {len(ground_truth_df)} ground truth records")

    # Create match keys for joining
    extracted_df['match_key'] = extracted_df['contract_id'].apply(
        lambda x: re.sub(r'[^A-Z0-9]', '', str(x).upper()) if pd.notna(x) else ""
    )
    ground_truth_df['match_key'] = ground_truth_df['contract_id_gt'].apply(
        lambda x: re.sub(r'[^A-Z0-9]', '', str(x).upper()) if pd.notna(x) else ""
    )

    # Merge on match key
    merged_df = pd.merge(ground_truth_df, extracted_df, on='match_key', how='left', suffixes=('_gt', '_ext'))

    # Compare fields
    validation_results = []

    for idx, row in merged_df.iterrows():
        gt_id = row.get('contract_id_gt', "")
        ext_id = row.get('contract_id', "")
        id_match = normalize(str(gt_id)) == normalize(str(ext_id)) if pd.notna(ext_id) else False

        gt_cost = row.get('contract_cost_gt', "")
        ext_cost = row.get('contract_cost', "")
        cost_match = normalize(str(gt_cost)) == normalize(str(ext_cost)) if pd.notna(ext_cost) else False

        gt_date = row.get('contract_date_gt', "")
        ext_date = row.get('contract_dates', "")
        if ext_date and '|' in str(ext_date):
            ext_date = str(ext_date).split('|')[0].strip()
        date_match = normalize(str(gt_date)) == normalize(str(ext_date)) if pd.notna(ext_date) else False

        gt_office = row.get('implementing_office_gt', "")
        ext_office = row.get('implementing_office', "")
        office_match = normalize(str(gt_office)) == normalize(str(ext_office)) if pd.notna(ext_office) else False

        validation_results.append({
            'record_id': row.get('record_id', f"GT_{idx}"),
            'region': row.get('region_gt', row.get('region', "")),
            'raw_sentence': row.get('raw_sentence', ""),
            'contract_id_ground_truth': gt_id,
            'contract_id_extracted': ext_id,
            'contract_id_match': id_match,
            'contract_cost_ground_truth': gt_cost,
            'contract_cost_extracted': ext_cost,
            'contract_cost_match': cost_match,
            'contract_date_ground_truth': gt_date,
            'contract_date_extracted': ext_date,
            'contract_date_match': date_match,
            'implementing_office_ground_truth': gt_office,
            'implementing_office_extracted': ext_office,
            'implementing_office_match': office_match,
        })

    result_df = pd.DataFrame(validation_results)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_excel(OUTPUT_FILE, index=False)

    print(f"\nValidation results saved to: {OUTPUT_FILE}")
    print(f"\nMatching Summary:")
    print(f"  Contract ID:       {result_df['contract_id_match'].sum():,} / {len(result_df):,}")
    print(f"  Contract Cost:     {result_df['contract_cost_match'].sum():,} / {len(result_df):,}")
    print(f"  Contract Date:     {result_df['contract_date_match'].sum():,} / {len(result_df):,}")
    print(f"  Implementing Off:  {result_df['implementing_office_match'].sum():,} / {len(result_df):,}")


if __name__ == "__main__":
    main()
