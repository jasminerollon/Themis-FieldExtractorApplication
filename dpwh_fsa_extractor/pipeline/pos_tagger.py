import pandas as pd
import spacy
from pathlib import Path

# Path Config
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_PATH = PROJECT_ROOT / "output" / "parallel_sentences.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "output" / "pos_tag_sequences.xlsx"

def load_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    return nlp


def get_pos_tags(sentence, nlp):
    if not sentence or not isinstance(sentence, str):
        return ""

    doc = nlp(sentence.strip())
    tags = [token.pos_ for token in doc if not token.is_space]
    return " ".join(tags)


def main():
    if not INPUT_PATH.exists():
        print(f"Error: Input file not found at {INPUT_PATH}")
        print("Please ensure Phase 1 & 2 are complete first.")
        return

    nlp = load_spacy_model()

    print(f"\nReading: {INPUT_PATH}")
    df = pd.read_excel(INPUT_PATH)
    print(f"Loaded {len(df)} sentence pairs")

    raw_pos_tags = []
    normalized_pos_tags = []

    for idx, row in df.iterrows():
        raw_sentence = row.get("raw_sentence", "")
        normalized_sentence = row.get("normalized_sentence", "")

        raw_pos_tags.append(get_pos_tags(raw_sentence, nlp))
        normalized_pos_tags.append(get_pos_tags(normalized_sentence, nlp))

        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(df)} sentences")

    output_df = pd.DataFrame({
        "region": df["region"],
        "raw_sentence": df["raw_sentence"],
        "raw_pos_tags": raw_pos_tags,
        "normalized_sentence": df["normalized_sentence"],
        "normalized_pos_tags": normalized_pos_tags
    })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_excel(OUTPUT_PATH, index=False)

    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Total sentences: {len(output_df)}")

if __name__ == "__main__":
    main()