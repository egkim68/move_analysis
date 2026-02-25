"""
BAMRC annotation pipeline using Google Gemini 2.0 Flash.
Supplementary material for: Kim, E. (2025). The Electronic Library.
Repository: https://github.com/egkim68/move_analysis

Requirements: pip install google-generativeai pandas
Input:  s12-clean.txt (one abstract per line)
Output: s12_gemini_bamrc.csv, s12_gemini_bamrc.txt, s12_gemini_bamrc_log.csv
"""

import pandas as pd
import time
import datetime
from google.generativeai import GenerativeModel, configure

# Configuration
INPUT_FILE = 's12-clean.txt'
OUTPUT_CSV = 's12_gemini_bamrc.csv'
OUTPUT_TXT = 's12_gemini_bamrc.txt'
MODEL_NAME = 'gemini-2.0-flash'

api_key = 'your-api-key-here'
configure(api_key=api_key)
model = GenerativeModel(MODEL_NAME)

# Prompt (see manuscript Section 3.3)
SYSTEM_PROMPT = """You will analyze journal article abstracts to identify BAMRC rhetorical components and tag each sentence appropriately.

There are SIX rhetorical components:
<1> Background - Establishes the research context, field importance, or general problem area
<2> Aim - States the study's specific purpose, objectives, or research questions
<3> Method - Describes the research approach, methodology, or data collection
<4> Results - Reports findings, outcomes, or key discoveries
<5> Conclusion - Discusses implications, significance, or future directions
<6> Undefined - Sentences that do not clearly fit into any of the above categories

INSTRUCTIONS:
- Tag each sentence with the appropriate number: <1>, <2>, <3>, <4>, <5>, or <6>
- Some components may appear multiple times
- Some components may be entirely absent
- Place the tag at the beginning of each sentence
- Do not add commentary or explanation

FORMAT EXAMPLE:
<1> Previous research has shown limited understanding of X.
<1> This problem affects many organizations.
<2> This study aims to examine the relationship between A and B.
<3> We conducted interviews with 50 participants.
<4> Results showed significant correlations.
<5> These findings have important implications for practice.

Return only the tagged abstract text using the format above."""


def load_abstracts_as_dataframe(input_file):
    print(f'Loading abstracts from: {input_file}')
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            abstracts = [line.strip() for line in f if line.strip()]
        df = pd.DataFrame({
            'doc_id': range(1, len(abstracts) + 1),
            'original_abstract': abstracts
        })
        print(f'Loaded {len(df)} abstracts (doc_id {df["doc_id"].min()}-{df["doc_id"].max()})')
        return df
    except FileNotFoundError:
        print(f'ERROR: File not found: {input_file}')
        return None
    except Exception as e:
        print(f'ERROR: {e}')
        return None


def get_gemini_response(user_prompt, max_retries=3, retry_delay=3):
    full_prompt = f'{SYSTEM_PROMPT}\n\n{user_prompt}'
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.1,
                    'max_output_tokens': 1000,
                    'top_p': 0.95
                }
            )
            return response.text
        except Exception as e:
            if attempt < max_retries - 1:
                print(f'  Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...')
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f'  Failed after {max_retries} attempts: {e}')
                return None


def process_abstracts_with_gemini(df):
    print(f'\nProcessing {len(df)} abstracts...')
    annotated_abstracts = []
    processing_status   = []

    for index, row in df.iterrows():
        doc_id   = row['doc_id']
        abstract = row['original_abstract']
        print(f'  doc_id {doc_id}/{len(df)}', end='')

        if not abstract or not abstract.strip():
            print(' - skipped (empty)')
            annotated_abstracts.append(None)
            processing_status.append('empty')
            continue

        annotated = get_gemini_response(f'Abstract: {abstract}')

        if annotated is not None:
            annotated_abstracts.append(annotated)
            processing_status.append('success')
            print(' - done')
        else:
            annotated_abstracts.append(None)
            processing_status.append('failed')
            print(' - failed')

        time.sleep(1.0)

    df['annotated_abstract'] = annotated_abstracts
    df['processing_status']  = processing_status

    success = processing_status.count('success')
    failed  = processing_status.count('failed')
    empty   = processing_status.count('empty')
    print(f'\nSuccess: {success}  Failed: {failed}  Empty: {empty}  ({success / len(df) * 100:.1f}%)')
    return df


def save_results(df, output_csv, output_txt):
    successful_df = df[df['processing_status'] == 'success'].copy()

    if successful_df.empty:
        print('ERROR: No successful annotations to save.')
        return None

    original_doc_ids = sorted(successful_df['doc_id'].tolist())

    missing = [x for x in range(1, df['doc_id'].max() + 1) if x not in original_doc_ids]
    if missing:
        print(f'WARNING: Missing doc_ids: {missing[:10]}{"..." if len(missing) > 10 else ""}')

    output_df = successful_df[['doc_id', 'original_abstract', 'annotated_abstract']].copy()
    assert list(output_df['doc_id']) == original_doc_ids, 'ERROR: doc_ids were modified!'
    output_df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f'CSV saved: {output_csv} ({len(output_df)} records)')

    with open(output_txt, 'w', encoding='utf-8') as f:
        for _, row in successful_df.sort_values('doc_id').iterrows():
            f.write(row['annotated_abstract'] + '\n')
    print(f'TXT saved: {output_txt}')

    log_file = output_csv.replace('.csv', '_log.csv')
    df.to_csv(log_file, index=False, encoding='utf-8')
    print(f'Log saved: {log_file}')

    return successful_df


def main():
    print('BAMRC Annotation Pipeline - Google Gemini 2.0 Flash')

    df = load_abstracts_as_dataframe(INPUT_FILE)
    if df is None:
        return

    df_processed = process_abstracts_with_gemini(df)
    final_df     = save_results(df_processed, OUTPUT_CSV, OUTPUT_TXT)

    if final_df is not None and not final_df.empty:
        print(f'\nDone. {len(final_df)} abstracts annotated at {datetime.datetime.now():%Y-%m-%d %H:%M:%S}')
    else:
        print('\nERROR: Pipeline failed.')


if __name__ == '__main__':
    main()
