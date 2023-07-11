from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
from utils.data_handler import FileHandler
from utils.key_phrase_extractor import Extractor
import pandas as pd
from datetime import datetime
import re
import argparse
from time import time

parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str, default='gpt-3.5-turbo')

args = parser.parse_args()

# get variables to be used.
today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
model = CompareText.model = args.model


def run_all():
    """Run Prism, from steps of accessing files to compare, key word search pre-filter step and comparison."""
    # # open specified files and get regulatory text cols.
    file_handler = FileHandler()
    reg_ref1, reg_corpus1, reg_ref2, reg_corpus2 = file_handler.get_reg_texts_cols()
    file1_name, file2_name = file_handler.get_files_names()

    # key phrase extractor. Get key phrases from reg text 2.
    print(f"\nFILTER STEP: Extracting key phrases from {file2_name} to search in {file1_name}")
    kp_extractor = Extractor()

    # extract key phrases from corpus 1 and find matching documents in corpus 2.
    filtered_ref_corpus1, filtered_ref_corpus2, non_matched_refs = kp_extractor.get_matching_records(reg_corpus1,
                                                                                                     reg_corpus2,
                                                                                                     reg_ref1,
                                                                                                     reg_ref2,
                                                                                                     log=True)
    filtered_corpus1 = [doc for doc in filtered_ref_corpus1.values()]
    filtered_corpus2 = [doc for doc in filtered_ref_corpus2.values()]
    filtered_ref1 = [ref for ref in filtered_ref_corpus1.keys()]
    filtered_ref2 = [ref for ref in filtered_ref_corpus2.keys()]

    """Comparator Block"""
    prompt = CompareText()

    # Instantiate lists to save outputs.
    text_1_list = []
    text_1_ref = []

    text_2_list = []
    text_2_ref = []

    explanations = []
    confidence_scores = []
    similarity_scores = []

    estimated_time = (1.5 * len(filtered_ref_corpus1) * len(filtered_ref_corpus2))/60
    n_comparisons = len(filtered_ref_corpus1) * len(filtered_ref_corpus2)


    print(f"\ncomparing {file1_name} to {file2_name} for an initial analysis. This will likely take {estimated_time} "
          f"minutes. If that is enough time, go enjoy a cup of coffee :)\n")

    for i, text1 in enumerate(filtered_corpus1):
        for j, text2 in enumerate(filtered_corpus2):

            comparison = prompt.compare_policies_prompt(text_1=text1, text_2=text2)
            dict_output = parse_stringified_json(comparison)
            explanations.append(dict_output['explanation'])
            confidence_scores.append(dict_output['confidence_score'])
            similarity_scores.append(dict_output['similarity_score'])
            text_1_list.append(text1)
            text_1_ref.append(filtered_ref1[i])
            text_2_list.append(text2)
            text_2_ref.append(filtered_ref2[j])

    # Create a dataframe of all matched comparisons.
    df = pd.DataFrame(data={f'{file1_name}_ref': text_1_ref,
                            f'{file1_name}_sample': text_1_list,
                            f'{file2_name}_ref': text_2_ref,
                            f'{file2_name}_sample': text_2_list,
                            'model_explanation': explanations,
                            'confidence_score': confidence_scores,
                            'similarity_score': similarity_scores
                            }).sort_values(by=['similarity_score', 'confidence_score'], ascending=False)

    print("\nSorting output to get results.")
    # partition dataframe based on aligned and partially aligned categories.
    aligned_df = df[df['similarity_score'] >= 0.7].copy()
    partial_df = df.loc[(df['similarity_score'] >= 0.5) &
                        (df['similarity_score'] < 0.7)].copy()

    # Provide a list of references from corpus2 that was not found in corpus1.
    non_matched_series = pd.DataFrame(data={
        f"{file2_name}_no_matches_refs":
            non_matched_refs
    })

    # output aligned and partial aligned text.
    output_file_name = f'sample_output_{model}_{today}'
    output_path = f"data/output/{output_file_name}.xlsx"

    with pd.ExcelWriter(output_path) as writer:
        aligned_df.to_excel(writer, sheet_name="Aligned", index=False)
        partial_df.to_excel(writer, sheet_name="Partial", index=False)
        non_matched_series.to_excel(writer, sheet_name="No_matches", index=False)
    print(f"\nOutput complete. Saved in {output_path}")


if __name__ == '__main__':
    t1 = time()
    print("Timer started.")
    run_all()
    t2 = (time() - t1)/60
    print(f"Mapping finished. Process took {t2:.2f} minutes.")
