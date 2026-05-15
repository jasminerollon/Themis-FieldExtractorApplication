import re
from collections import defaultdict
from itertools import product
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
POS_TAG_INPUT_PATH = PROJECT_ROOT / "output" / "pos_tag_sequences.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "output" / "nfold_product.xlsx"

FIELD_TYPES = ["contract_id", "contract_cost", "contract_dates", "implementing_office"]
EXCEL_ROW_LIMIT = 1_048_576 - 1

# Pre-compiled patterns (classify once per row)
_RE_CONTRACT_ID = re.compile(r"\b\d{2}[A-Za-z]{1,2}\d{4,5}\b", re.IGNORECASE)
_RE_COST = re.compile(r"\b\d{1,3}(?:,\d{3})*\.\d{2}\b")
_MONTHS = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
)
_RE_DATE = re.compile(rf"\b{_MONTHS}\s+\d{{1,2}},\s+\d{{4}}\b")
_RE_OFFICE = re.compile(
    r"District Engineering Office|\bDEO\b|"
    r"Region\s+(?:[IVXLCDM]+|\d+|NCR|CAR|NIR|BARMM)",
    re.IGNORECASE,
)


def safe_str(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value)


def classify_field_type(raw_sentence: str) -> str:
    if not raw_sentence:
        return "other"
    if _RE_CONTRACT_ID.search(raw_sentence):
        return "contract_id"
    if _RE_COST.search(raw_sentence):
        return "contract_cost"
    if _RE_DATE.search(raw_sentence):
        return "contract_dates"
    if _RE_OFFICE.search(raw_sentence):
        return "implementing_office"
    return "other"


def pairs_from_columns(tokens_str: str, tags_str: str) -> list[tuple[str, str]]:
    """Build (word, pos_tag) pairs from precomputed token/tag columns (no spaCy)."""
    tokens = safe_str(tokens_str).split()
    tags = safe_str(tags_str).split()
    if not tokens or not tags:
        return []
    # spaCy token count should match tag count; use the shorter span if not.
    n = min(len(tokens), len(tags))
    return list(zip(tokens[:n], tags[:n]))


def triples_for_row(
    source_pairs: list[tuple[str, str]],
    target_pairs: list[tuple[str, str]],
) -> list[tuple[str, str, str]]:
    """Ws × T × Wt using itertools.product (faster than nested Python loops)."""
    target_words = [wt for wt, _ in target_pairs]
    return [
        (ws, pos_tag, wt)
        for ws, pos_tag in source_pairs
        for wt in target_words
    ]


def main():
    print("=" * 60)
    print("N-Fold Product Builder - Deliverable 3")
    print("=" * 60)

    if not POS_TAG_INPUT_PATH.exists():
        print(f"Error: Input file not found at {POS_TAG_INPUT_PATH}")
        print("Please run pos_tagger.py first.")
        return

    print(f"\nReading: {POS_TAG_INPUT_PATH}")
    df = pd.read_excel(POS_TAG_INPUT_PATH)
    df = df.fillna("")
    print(f"Loaded {len(df):,} sentence pairs")

    has_token_cols = "raw_tokens" in df.columns and "normalized_tokens" in df.columns
    if not has_token_cols:
        print(
            "Warning: raw_tokens / normalized_tokens columns missing.\n"
            "Re-run pos_tagger.py for best performance (avoids slow re-tokenization)."
        )

    # Vectorized field classification before the hot loop
    raw_sentences = df["raw_sentence"].map(safe_str)
    df["field_type"] = raw_sentences.map(classify_field_type)
    candidate = df[df["field_type"].isin(FIELD_TYPES)]
    print(f"Rows matching a target field type: {len(candidate):,} / {len(df):,}")

    # field_type -> set of (w_source, pos_tag, w_target) for dedup during accumulation
    triple_sets: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    processed = 0

    for row in candidate.itertuples(index=False):
        field_type = row.field_type

        source_pairs = pairs_from_columns(
            row.raw_tokens if has_token_cols else "",
            row.raw_pos_tags,
        )
        target_pairs = pairs_from_columns(
            row.normalized_tokens if has_token_cols else "",
            row.normalized_pos_tags,
        )

        if not source_pairs or not target_pairs:
            continue

        for triple in triples_for_row(source_pairs, target_pairs):
            triple_sets[field_type].add(triple)

        processed += 1
        if processed % 500 == 0:
            print(f"  Processed {processed:,} field rows...")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    total_written = 0

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        for field_type in FIELD_TYPES:
            triples = triple_sets.get(field_type, set())
            if not triples:
                pd.DataFrame(
                    columns=["field_type", "w_source", "pos_tag", "w_target"]
                ).to_excel(writer, sheet_name=field_type[:31], index=False)
                continue

            sheet_df = pd.DataFrame(
                [
                    {
                        "field_type": field_type,
                        "w_source": ws,
                        "pos_tag": pos_tag,
                        "w_target": wt,
                    }
                    for ws, pos_tag, wt in triples
                ],
                columns=["field_type", "w_source", "pos_tag", "w_target"],
            )

            print(f"  {field_type}: {len(sheet_df):,} unique triples")

            if len(sheet_df) > EXCEL_ROW_LIMIT:
                print(
                    f"  WARNING: truncating {field_type} to {EXCEL_ROW_LIMIT:,} rows. "
                    "Consider exporting large sheets as CSV."
                )
                sheet_df = sheet_df.iloc[:EXCEL_ROW_LIMIT]

            sheet_df.to_excel(writer, sheet_name=field_type[:31], index=False)
            total_written += len(sheet_df)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Total triples written: {total_written:,}")

    print("\nSummary by field type:")
    for field_type in FIELD_TYPES:
        print(f"  {field_type}: {len(triple_sets.get(field_type, set())):,} unique triples")


if __name__ == "__main__":
    main()
