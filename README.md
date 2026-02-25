# BAMRC Rhetorical Move Annotation — Supplementary Materials

Supplementary data and scripts for:

> Kim, E. (2026). From manual to automated: Applying large language models to rhetorical move analysis in journal abstracts. *The Electronic Library*.

## Contents

| File | Description |
|------|-------------|
| `dataset_human.csv` | Bibliographic metadata and human-coded move sequences (Kim, 2014) |
| `dataset_claude.csv` | Bibliographic metadata and move sequences annotated by Claude 3.5 Haiku |
| `dataset_openai.csv` | Bibliographic metadata and move sequences annotated by GPT-4o Mini |
| `dataset_gemini.csv` | Bibliographic metadata and move sequences annotated by Gemini 2.0 Flash |
| `dataset_deepseek.csv` | Bibliographic metadata and move sequences annotated by DeepSeek Chat |
| `moves-claude.py` | Annotation pipeline script — Claude 3.5 Haiku |
| `moves-openai.py` | Annotation pipeline script — GPT-4o Mini |
| `moves-gemini.py` | Annotation pipeline script — Gemini 2.0 Flash |
| `moves-deepseek.py` | Annotation pipeline script — DeepSeek Chat |

## Data

Each dataset contains bibliographic metadata (article ID, citation, first sentence) and BAMRC rhetorical move sequences for 415 social science abstracts retrieved from Scopus (keyword: "attitude", 2012–2014). Full abstract texts are not included due to Scopus licensing restrictions. The corpus can be reconstructed using the search parameters described in Section 3.1 of the manuscript.

BAMRC categories: 1 = Background, 2 = Aim, 3 = Method, 4 = Results, 5 = Conclusion, 6 = Undefined.

## Scripts

Each script processes a plain-text file of abstracts (`s12-clean.txt`, one per line) and returns sentence-level BAMRC annotations via the respective model API. See Section 3.2–3.3 of the manuscript for model configuration and prompt details.

**Requirements**

```
pip install anthropic pandas        # moves-claude.py
pip install openai pandas           # moves-openai.py, moves-deepseek.py
pip install google-generativeai pandas  # moves-gemini.py
```

Replace `your-api-key-here` in each script with a valid API key before running.
