from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
from utils.data_handler import FileHandler
from utils.key_phrase_extractor import Extractor
import pandas as pd
from datetime import datetime
import re
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str, default='gpt-3.5-turbo')

args = parser.parse_args()


def run_all():
    today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
    model = CompareText.model = args.model
    prompt = CompareText()

    # # open specified files and get regulatory text cols.
    file_handler = FileHandler()
    reg_ref1, reg_corpus1, reg_ref2, reg_corpus2 = file_handler.get_reg_texts_cols()
    file1_name, file2_name = file_handler.get_files_names()

    # key phrase extractor. Get key phrases from reg text 2.
    print("Extracting key phrases from regulation text 2")
    kp_extractor = Extractor()

    # extract key phrases from corpus 1 and find matching documents in corpus 2.
    filtered_ref_corpus1, filtered_ref_corpus2, non_matched_refs = kp_extractor.get_matching_records(reg_corpus1,
                                                                                                     reg_corpus2,
                                                                                                     reg_ref1,
                                                                                                     reg_ref2)

    filtered_corpus1 = [doc for doc in filtered_ref_corpus1.values()]
    filtered_corpus2 = [doc for doc in filtered_ref_corpus2.values()]
    filtered_ref1 = [ref for ref in filtered_ref_corpus1.keys()]
    filtered_ref2 = [ref for ref in filtered_ref_corpus2.keys()]

    # Comparator block.
    text_1_list = []
    text_1_ref = []

    text_2_list = []
    text_2_ref = []

    explanations = []
    confidence_scores = []
    similarity_scores = []

    for i, text1 in enumerate(filtered_corpus1):
        for j, text2 in enumerate(filtered_corpus2):
            print(f"comparing {file1_name} policy {i + 1} to {file2_name} policy {j + 1}")
            comparison = prompt.compare_texts_prompt(text_1=text1, text_2=text2)
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

    # partition dataframe based on aligned and partially aligned categories.
    aligned_df = df[df['similarity_score'] >= 0.7].copy()
    partial_df = df.loc[(df['similarity_score'] >= 0.5) &
                        (df['similarity_score'] < 0.7)].copy()

    # output aligned and partial aligned text.
    output_file_name = f'sample_output_{model}_{today}'
    output_path = f"data/output/{output_file_name}"

    aligned_df.to_excel(f"{output_path}_aligned.xlsx", sheet_name="Aligned", index=False)
    partial_df.to_excel(f"{output_path}_partial.xlsx", sheet_name="Partial", index=False)

    # Provide a list of references from corpus2 that was not found in corpus1.
    non_matched_series = pd.DataFrame(data={
                                            f"{file2_name}_no_matches_refs":
                                            non_matched_refs
                                            })
    non_matched_series.to_excel(f"{output_path}_not_aligned.xlsx", sheet_name="no_matches", index=False)


if __name__ == '__main__':
    run_all()
