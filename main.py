from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
from utils.data_handler import FileHandler
from utils.key_phrase_extractor import Extractor
import pandas as pd
from datetime import datetime
import re
import argparse
from time import time
from tqdm import tqdm
import csv

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
    refs_completed = []

    print(f"\ncomparing {file1_name} to {file2_name} for an initial analysis. Go enjoy a cup of coffee while PRISM"
          f" gets things done for you :)\n")

    # set up output path
    output_file_name = f'{file1_name}_{file2_name}_{model}_{today}'
    backup_folder_path = 'data/backup/'
    backup_file = open(f'{backup_folder_path}{output_file_name}_backup.csv', 'w')
    backup_file.write(f"ref1, {file1_name}, ref2, {file2_name}, model_explanation, confidence_score, similarity_score")
    backup_file.close()
    backup_file = open(f'{backup_folder_path}{output_file_name}_backup.csv', 'a')

    try:
        for i, text1 in enumerate(tqdm(filtered_corpus1)):
            for j, text2 in enumerate(filtered_corpus2):
                comparison = prompt.compare_policies_prompt(text_1=text1, text_2=text2)
                dict_output = parse_stringified_json(comparison)

                # Keep variables of all the bits that need to be written.
                ref1 = filtered_ref1[i]
                text1_backup = text1.replace(',', '')
                ref2 = filtered_ref2[j]
                text2_backup = text2.replace(',', '')
                explanation = dict_output['explanation']
                explanation_backup = explanation.replace(',', '')
                confidence_score = dict_output['confidence_score']
                similarity_score = dict_output['similarity_score']

                # write to backup csv file.
                backup_file.write(f"\n{ref1}, {text1_backup}, {ref2}, {text2_backup}, {explanation_backup}, "
                                  f"{confidence_score}, {similarity_score}")

                # store in lists to write to final excel file.
                explanations.append(explanation)
                confidence_scores.append(confidence_score)
                similarity_scores.append(similarity_score)
                text_1_list.append(text1)
                text_1_ref.append(ref1)
                text_2_list.append(text2)
                text_2_ref.append(ref2)
    except:
        backup_file.close()
        print(f"The programme failed, however all the completed refs for {file1_name} are saved in f'{backup_folder_path}{output_file_name}_backup.csv")
        raise

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
    # # partition dataframe based on aligned and partially aligned categories.
    main_output_df = df.sort_values(by=['similarity_score', 'confidence_score']).copy()

    # Provide a list of references from corpus2 that was not found in corpus1.
    non_matched_series = pd.DataFrame(data={
        f"{file2_name}_no_matches_refs":
            non_matched_refs
    })

    # output aligned and partial aligned text.
    output_path = f"data/output/{output_file_name}.xlsx"

    with pd.ExcelWriter(output_path) as writer:
        main_output_df.to_excel(writer, sheet_name="matches", index=False)
        non_matched_series.to_excel(writer, sheet_name="NA", index=False)
    print(f"\nOutput complete. Saved in {output_path}")


if __name__ == '__main__':
    t1 = time()
    print("Timer started.")
    run_all()
    t2 = (time() - t1) / 60
    print(f"Mapping finished. Process took {t2:.2f} minutes.")
