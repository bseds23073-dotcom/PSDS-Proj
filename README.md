# Know Your Data: Under-5 mortality in South Asia (WDI, 2000-2023)

Part A of Assignment 1, Problem Solving with Data Science (ITU, Fall 2026).
Partners: Mustafa Shahid, Ayan Mahmood

## How to reproduce
1. `pip install -r requirements.txt`
2. The untouched World Bank extract is in `data/raw/` (see `data/raw/README.md`).
3. `python src/load_and_reshape.py` (raw -> long and panel format, no cleaning decisions)
4. `python src/clean_and_eda.py` (checks, cleaning decisions, charts, confounder check, baseline models), or open `notebooks/01_cleaning_eda.ipynb` and run it top to bottom.
Run both commands from the repository root. Printed results are saved in `reports/analysis_output.txt`; charts are in `figures/`.

## Files
PROPOSAL_v2.md, ACQUISITION.md, FIVE_QUESTIONS.md, CLEANING.md, DATA_DICTIONARY.md, EDA_NOTES.md, JOURNAL.md, LIMITATIONS.md, CONTRIBUTIONS.md, AI_USE_LOG.md
