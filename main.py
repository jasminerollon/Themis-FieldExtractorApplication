import sys
from dpwh_fsa_extractor.pipeline import (
    pdf_extractor,
    preprocessor,
    pos_tagger,
    nfold_builder,
    field_extractor
)
from dpwh_fsa_extractor.evaluation import metrics, validate_extraction

def main():
    print("=" * 60)
    print("Themis-FieldExtractorApplication Pipeline")
    print("Note: Runs pdf_extractor on both 2024 and 2023 PDFs,")
    print("derives grammars and FSAs from 2024, then applies FSAs to")
    print("both corpora. 2023 corpus is used for evaluation.")
    print("=" * 60)

    try:
        # Phase 1: PDF Extraction
        print("\n[1/7] Running PDF Extractor...")
        pdf_extractor.main()

        # Phase 2: Preprocessor
        print("\n[2/7] Running Preprocessor...")
        preprocessor.generate_parallel_sentences_excel()

        # Phase 3: POS Tagger
        print("\n[3/7] Running POS Tagger...")
        pos_tagger.main()

        # Phase 4: N-Fold Builder
        print("\n[4/7] Running N-Fold Builder...")
        nfold_builder.main()

        # Phase 5: Field Extractor
        print("\n[5/7] Running Field Extractor...")
        field_extractor.main()

        # Phase 6: Metrics & Evaluation
        print("\n[6/7] Running Metrics Evaluation...")
        metrics.main()

        # Phase 7: Validation Results
        print("\n[7/7] Generating Detailed Validation Results...")
        validate_extraction.main()

        print("\n" + "=" * 60)
        print("Pipeline execution completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nPipeline failed with error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
