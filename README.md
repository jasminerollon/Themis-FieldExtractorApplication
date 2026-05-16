# Themis — DPWH Field Extractor

**Themis** is an automaton-driven field extraction system for Department of Public Works and Highways (DPWH) infrastructure transparency reports. It applies formally specified finite state automata (FSAs) derived from right-linear grammars to recognize and validate four target administrative fields from digitally encoded stakeholder PDFs:
## Team & course

Saint Louis University — CS 223 Automata and Formal Languages (AY 2025–2026).

### Project by:
ADVINCULA, Ellouise <br>
POLO, Wayllene Kalina <br>
RAMOS, Rhinnoa Chloe <br>
ROLLON, Jasmine <br>
SARQUILLA, Christine Abigail

---
| Field | Example surface form |
|-------|----------------------|
| Contract ID | `24PA0001` |
| Contract Cost | `4,706,352.51` |
| Contract Dates | `February 19, 2024` |
| Implementing Office | `Abra District Engineering Office` |

The project supports CS 223 (Automata and Formal Languages) research on corpus-driven grammar design, parallel corpus construction, POS tagging, and cross-validation against the [BetterGovPH DPWH transparency dataset](https://data.bettergov.ph/datasets/19).

---

## How it works

The pipeline runs in phases:

```text
PDFs (data/raw)
    → pdf_extractor.py        → plain text per region (data/extracted)
    → preprocessor.py         → parallel_sentences.xlsx
    → pos_tagger.py           → pos_tag_sequences.xlsx
    → nfold_builder.py        → nfold_product.csv
    → field_extractor.py      → extracted_fields.xlsx
    → metrics.py              → console evaluation metrics
    → validate_extraction.py   → validation_results.xlsx (detailed match analysis)
```

Each target field has a dedicated DFA in `dpwh_fsa_extractor/fsa/`. Formal grammar constants live in `dpwh_fsa_extractor/grammars/grammar_definitions.py` and mirror the project paper.

All FSAs expose the shared interface:

```python
def run_fsa(token_string: str) -> dict:
    # Returns {"matched": bool, "value": str}
```

---

## Requirements

- Python 3.10+ (3.14 tested)
- Dependencies in `requirements.txt`:
  - `pdfplumber` — PDF table extraction
  - `pandas`, `openpyxl` — Excel deliverables
  - `spacy` — POS tagging (Universal Dependencies tagset)

---

## Setup

Clone the repository and install dependencies:

```powershell
cd Themis-FieldExtractorApplication
py -m pip install -r requirements.txt
py -m spacy download en_core_web_sm
```

### Input data

1. **Regional PDFs** — Place CY 2024 stakeholder reports in:

   ```
   dpwh_fsa_extractor/data/raw/
   ```

   Filenames must match the list in `pdf_extractor.py` (e.g. `DPWH-NCR-INFRA.pdf`).

2. **Validation CSV** — The BetterGovPH reference file should be at:

   ```
   dpwh_fsa_extractor/data/validation/dpwh_transparency_data.csv
   ```

---

## Running the pipeline

You can execute the entire pipeline using the main script, or run individual phases sequentially.

### Option A: Run the Complete Pipeline

To run all phases (extraction, preprocessing, POS tagging, N-fold building, field extraction, metrics, and detailed validation) in sequence:

```powershell
py main.py
```
*(Or `python main.py` depending on your environment)*

This master runner will handle all outputs from `data/raw` through extraction, tagging, model training data generation, field extraction, and validation. Final outputs include `validation_results.xlsx` (detailed per-record match analysis) and comprehensive evaluation metrics in your console.

### Option B: Run Individual Phases

Run each stage from the project root using the `py` launcher:

### 1. Extract text from PDFs

```powershell
py -m dpwh_fsa_extractor.pipeline.pdf_extractor
```

Output: `dpwh_fsa_extractor/data/extracted/*.txt`

### 2. Preprocess and build parallel corpus (Deliverable 1)

```powershell
py -m dpwh_fsa_extractor.pipeline.preprocessor
```

Output: `dpwh_fsa_extractor/output/parallel_sentences.xlsx`

Columns: `region`, `raw_sentence`, `normalized_sentence`

### 3. POS tagging (Deliverable 2)

```powershell
py -m dpwh_fsa_extractor.pipeline.pos_tagger
```

Output: `dpwh_fsa_extractor/output/pos_tag_sequences.xlsx`

Columns include `raw_tokens`, `raw_pos_tags`, `normalized_tokens`, `normalized_pos_tags` (UD tagset via `token.tag_`). Uses batched `nlp.pipe()` with parser/NER disabled for speed.

### 4. N-fold product set (Deliverable 3)

```powershell
py -m dpwh_fsa_extractor.pipeline.nfold_builder
```

Output: `dpwh_fsa_extractor/output/nfold_product.csv` (CSV format for large datasets)

Columns: `field_type`, `w_source`, `pos_tag`, `w_target`

Contains ~2.7M training triples for ML models, segregated by field type with POS tags for each source-target word pair.

### 5. Field Extraction (FSA Execution)

```powershell
py -m dpwh_fsa_extractor.pipeline.field_extractor
```

Output: `dpwh_fsa_extractor/output/extracted_fields.xlsx`

Applies the formal grammar FSAs to extract the specific fields from the text.

### 6. Validation and Metrics Evaluation

```powershell
py -m dpwh_fsa_extractor.evaluation.metrics
```

Output: Console evaluation metrics (FSA test case validation, extraction success rates, per-field accuracy)

Displays both FSA pattern validation (test cases) and real data extraction accuracy against ground truth.

### 7. Detailed Validation Results (Excel Report)

```powershell
py -m dpwh_fsa_extractor.evaluation.validate_extraction
```

Output: `dpwh_fsa_extractor/output/validation_results.xlsx`

Columns: `record_id`, `region`, `contract_id_ground_truth`, `contract_id_extracted`, `contract_id_match`, `contract_cost_*`, `contract_date_*`, `implementing_office_*` (expanded for all fields)

Creates a detailed row-by-row comparison of all ground truth records against extracted values. Use this Excel file for paper/report documentation.

### Testing FSAs directly

```powershell
py -c "from dpwh_fsa_extractor.fsa.fsa_contract_id import run_fsa; print(run_fsa('24PA0001'))"
```

---

## Project structure

```text
Themis-FieldExtractorApplication/
├── main.py                          # Master runner
├── requirements.txt
├── README.md
└── dpwh_fsa_extractor/
    ├── grammars/
    │   └── grammar_definitions.py   # G1–G4 formal specs
    ├── fsa/
    │   ├── fsa_contract_id.py
    │   ├── fsa_contract_cost.py
    │   ├── fsa_contract_dates.py
    │   └── fsa_implementing_office.py
    ├── pipeline/
    │   ├── pdf_extractor.py
    │   ├── preprocessor.py
    │   ├── pos_tagger.py
    │   ├── nfold_builder.py
    │   └── field_extractor.py
    ├── evaluation/
    │   ├── metrics.py               # Console validation metrics
    │   └── validate_extraction.py   # Excel validation report
    ├── data/
    │   ├── raw/                     # Regional PDFs (local only)
    │   ├── extracted/               # Generated .txt files
    │   └── validation/              # Ground truth CSV
    └── output/                      # Excel & CSV deliverables
```

---

## Grammar reference (G1–G4)

| Grammar | Pattern | Module |
|---------|---------|--------|
| G1 | `dd(l \| ll)(dddd \| ddddd)` | `fsa_contract_id.py` |
| G2 | `(n \| nn \| nnn)(,nnn)*(.nn)` | `fsa_contract_cost.py` |
| G3 | Month day, year (long-form) | `fsa_contract_dates.py` |
| G4 | DEO / ordinal DEO / Region roman / NCR, CAR, NIR | `fsa_implementing_office.py` |

Implementing-office G4 accepts:

- Full district names — `Abra District Engineering Office`
- Abbreviated DEO — `Cotabato 1st DEO`, `Abra DEO`
- Numbered regions — `Region VII`
- Special regions — `NCR`, `CAR`, `NIR`

---
