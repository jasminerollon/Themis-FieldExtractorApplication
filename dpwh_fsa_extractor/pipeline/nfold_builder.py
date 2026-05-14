import pandas as pd
import spacy
import re
from pathlib import Path
from collections import defaultdict

# Path Config
PROJECT_ROOT = Path(__file__).parent.parent
POS_TAG_INPUT_PATH = PROJECT_ROOT / "output" / "pos_tag_sequences.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "output" / "nfold_product.xlsx"

FIELD_TYPES = ["contract_id", "contract_cost", "contract_dates", "implementing_office"]

def load_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    return nlp


def safe_str(value):
    if pd.isna(value) or value is None:
        return ""
    return str(value)


def classify_field_type(raw_sentence, normalized_sentence):
    raw_sentence = safe_str(raw_sentence)
    normalized_sentence = safe_str(normalized_sentence)

    if not raw_sentence or not normalized_sentence:
        return "other"

    contract_id_pattern = r'\b\d{2}[A-Za-z]{1,2}\d{4,5}\b'

    cost_pattern = r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b'

    months = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    date_pattern = rf'\b{months}\s+\d{{1,2}},\s+\d{{4}}\b'

    office_patterns = [
        r'District Engineering Office',
        r'\bDEO\b',
        r'Region\s+(?:[IVXLCDM]+|\d+|NCR|CAR|NIR|BARMM)'
    ]

    if re.search(contract_id_pattern, raw_sentence, re.IGNORECASE):
        return "contract_id"
    elif re.search(cost_pattern, raw_sentence):
        return "contract_cost"
    elif re.search(date_pattern, raw_sentence):
        return "contract_dates"
    elif any(re.search(p, raw_sentence, re.IGNORECASE) for p in office_patterns):
        return "implementing_office"
    else:
        return "other"


def tokenize_with_pos(sentence, pos_tags_str, nlp):
    sentence = safe_str(sentence)
    pos_tags_str = safe_str(pos_tags_str)

    if not sentence or not pos_tags_str:
        return []

    doc = nlp(sentence.strip())
    pos_tags = pos_tags_str.split()

    aligned = []
    token_idx = 0
    for token in doc:
        if not token.is_space:
            if token_idx < len(pos_tags):
                aligned.append((token.text, pos_tags[token_idx]))
            token_idx += 1

    return aligned


def build_cartesian_product(source_pairs, target_pairs):
    product = []

    for ws, pos_tag in source_pairs:
        for wt, _ in target_pairs:
            product.append((ws, pos_tag, wt))

    return product


def main():
    print("=" * 60)
    print("N-Fold Product Builder - Deliverable 3")
    print("=" * 60)

    if not POS_TAG_INPUT_PATH.exists():
        print(f"Error: Input file not found at {POS_TAG_INPUT_PATH}")
        print("Please run pos_tagger.py first.")
        return

    nlp = load_spacy_model()

    print(f"\nReading: {POS_TAG_INPUT_PATH}")
    df = pd.read_excel(POS_TAG_INPUT_PATH)
    print(f"Loaded {len(df)} sentence pairs")

    df = df.fillna("")

    all_triples = defaultdict(list)

    for idx, row in df.iterrows():
        raw_sentence = row.get("raw_sentence", "")
        raw_pos_tags = row.get("raw_pos_tags", "")
        normalized_sentence = row.get("normalized_sentence", "")
        normalized_pos_tags = row.get("normalized_pos_tags", "")

        if not raw_sentence or not normalized_sentence:
            continue

        field_type = classify_field_type(raw_sentence, normalized_sentence)

        if field_type not in FIELD_TYPES:
            continue

        source_pairs = tokenize_with_pos(raw_sentence, raw_pos_tags, nlp)
        target_pairs = tokenize_with_pos(normalized_sentence, normalized_pos_tags, nlp)

        if not source_pairs or not target_pairs:
            continue

        triples = build_cartesian_product(source_pairs, target_pairs)

        for ws, pos_tag, wt in triples:
            all_triples[field_type].append({
                "field_type": field_type,
                "w_source": ws,
                "pos_tag": pos_tag,
                "w_target": wt
            })

        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(df)} sentences")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_written = 0
    EXCEL_ROW_LIMIT = 1_048_576 - 1

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        for field_type in FIELD_TYPES:
            records = all_triples.get(field_type, [])
            if not records:
                sheet_df = pd.DataFrame(columns=["field_type", "w_source", "pos_tag", "w_target"])
                sheet_df.to_excel(writer, sheet_name=field_type[:31], index=False)
                continue

            sheet_df = pd.DataFrame(records, columns=["field_type", "w_source", "pos_tag", "w_target"])

            before = len(sheet_df)
            sheet_df = sheet_df.drop_duplicates()
            after = len(sheet_df)
            print(f"  {field_type}: {before} → {after} triples after deduplication")

            if len(sheet_df) > EXCEL_ROW_LIMIT:
                print(f"  WARNING: {field_type} still has {len(sheet_df)} rows after dedup. "
                      f"Truncating to {EXCEL_ROW_LIMIT}. Consider saving as CSV instead.")
                sheet_df = sheet_df.iloc[:EXCEL_ROW_LIMIT]

            sheet_df.to_excel(writer, sheet_name=field_type[:31], index=False)
            total_written += len(sheet_df)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Total triples written: {total_written}")

    print("\nSummary by field type:")
    for field_type in FIELD_TYPES:
        records = all_triples.get(field_type, [])
        count = len(pd.DataFrame(records).drop_duplicates()) if records else 0
        print(f"  {field_type}: {count} unique triples")

if __name__ == "__main__":
    main()