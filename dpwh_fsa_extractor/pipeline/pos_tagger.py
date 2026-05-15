import pandas as pd
import spacy
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_PATH = PROJECT_ROOT / "output" / "parallel_sentences_2024.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "output" / "pos_tag_sequences_2024.xlsx"

# Larger batches amortize spaCy overhead; lower if memory is tight.
BATCH_SIZE = 512


def load_spacy_model():
    """Tagger-only pipeline: skip parser/NER/lemmatizer for much faster tagging."""
    try:
        nlp = spacy.load(
            "en_core_web_sm",
            disable=["parser", "ner", "attribute_ruler", "lemmatizer"],
        )
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load(
            "en_core_web_sm",
            disable=["parser", "ner", "attribute_ruler", "lemmatizer"],
        )
    return nlp


def _prepare_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def tag_column(texts: list[str], nlp) -> tuple[list[str], list[str]]:
    """Batch-tag sentences; returns parallel token, tag, and token columns."""
    token_cols: list[str] = []
    tag_cols: list[str] = []

    prepared = [_prepare_text(t) for t in texts]
    for doc in nlp.pipe(prepared, batch_size=BATCH_SIZE):
        tokens = [t.text for t in doc if not t.is_space]
        tags = [t.tag_ for t in doc if not t.is_space]
        token_cols.append(" ".join(tokens))
        tag_cols.append(" ".join(tags))

    return token_cols, tag_cols


def main():
    if not INPUT_PATH.exists():
        print(f"Error: Input file not found at {INPUT_PATH}")
        print("Please ensure Phase 1 & 2 are complete first.")
        return

    nlp = load_spacy_model()

    print(f"\nReading: {INPUT_PATH}")
    df = pd.read_excel(INPUT_PATH)
    print(f"Loaded {len(df):,} sentence pairs")

    raw_texts = df["raw_sentence"].tolist()
    norm_texts = df["normalized_sentence"].tolist()

    print(f"Tagging raw sentences (batch_size={BATCH_SIZE})...")
    raw_tokens, raw_pos_tags = tag_column(raw_texts, nlp)

    print(f"Tagging normalized sentences (batch_size={BATCH_SIZE})...")
    norm_tokens, norm_pos_tags = tag_column(norm_texts, nlp)

    output_df = pd.DataFrame({
        "region": df["region"],
        "raw_sentence": df["raw_sentence"],
        "raw_tokens": raw_tokens,
        "raw_pos_tags": raw_pos_tags,
        "normalized_sentence": df["normalized_sentence"],
        "normalized_tokens": norm_tokens,
        "normalized_pos_tags": norm_pos_tags,
    })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_excel(OUTPUT_PATH, index=False)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Total sentences: {len(output_df):,}")


if __name__ == "__main__":
    main()
