from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
from utils.key_phrase_extractor import Extractor
from utils.output_funcs import model_judgment_criteria
import pandas as pd
from datetime import datetime
import re
import argparse
from time import time
from tqdm import tqdm
import streamlit as st

parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str, default='gpt-3.5-turbo')

args = parser.parse_args()

# get variables to be used.
today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
model = CompareText.model = args.model


def create_backup_file(file1, file2, model_name, datetime):
    """
    Create a backup file to save in case run is interrupted.
    :param file1: Base/reference regulatory text file, e.g. Dora.
    :param file2: Comparison text file name.
    :param model_name: model to be used, saved as a record - e.g. gpt-3.5-turbo
    :param datetime: Version/tracking information.
    :return: a file base to write on.
    """
    output_file_name = f'{file1}_{file2}_{model_name}_{datetime}'
    backup_folder_path = 'data/backup/'
    backup_file = open(f'{backup_folder_path}{output_file_name}_backup.csv', 'w')
    backup_file.write(f"ref1, {file1}, ref2, {file2}, model_explanation, confidence_score, similarity_score")
    backup_file.close()
    backup_file = open(f'{backup_folder_path}{output_file_name}_backup.csv', 'a')

    return backup_file


# Function to read and process the uploaded files
def process_reg_files(file_1, file_2):
    df_1 = pd.read_excel(file_1)
    df_2 = pd.read_excel(file_2)

    # extract out the reg ref and regulation text.
    regulation_ref1_col = df_1[df_1.columns[0]]
    regulation_text1_col = df_1.columns[1]
    regulation1_text = df_1[
        regulation_text1_col].apply(lambda x: x.replace('\n', ''))
    # free up memory
    del df_1

    regulation_ref2_col = df_2[df_2.columns[0]]
    regulation_text2_col = df_2.columns[1]
    regulation2_text = df_2[
        regulation_text2_col].apply(lambda x: x.replace('\n', ''))
    # free up memory.
    del df_2

    return regulation_ref1_col, regulation1_text, regulation_ref2_col, regulation2_text


# Streamlit app
def main():
    """Run Prism, from steps of accessing files to compare, key word search pre-filter step and comparison."""
    # # open specified files and get regulatory text cols.

    # streamlit app
    st.title("                                                         PRISM")
    st.write("Please upload up to 2 .xlsx files containing the regulation ref and texts.")

    # Allow file uploads
    uploaded_files = st.file_uploader(
        label="Upload your .xlsx files",
        type=["xlsx"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    # ensuring that two files are uploaded.
    if uploaded_files and len(uploaded_files) == 2:
        if st.button("Run Prism"):

            # storing the names of the files.
            file1_name = uploaded_files[0].name
            file2_name = uploaded_files[1].name
            # Process files and show progress bar when 'Run Prism' button is clicked
            reg_ref1, reg_corpus1, reg_ref2, reg_corpus2 = process_reg_files(uploaded_files[0], uploaded_files[1])

            st.write("Timer started.")
            t1 = time()
            # key phrase extractor. Get key phrases from reg text 2.
            st.write(f"\nFILTER STEP:")
            st.write(f"\nExtracting key phrases from {file2_name} to search in {file1_name}")

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

            """COMPARATOR BLOCK:"""

            st.write(f"")

            prompt = CompareText()

            # Instantiate lists to save outputs.
            text_1_list = []
            text_1_ref = []

            text_2_list = []
            text_2_ref = []

            explanations = []
            confidence_scores = []
            similarity_scores = []

            st.write(f"\nComparing {file1_name} to {file2_name} for an initial analysis.")
            st.write(f"\nGo enjoy a cup of coffee while PRISM gets things done for you :)")

            # set up back up file to write on.
            backup_file = create_backup_file(file1_name, file2_name, model_name=model, datetime=today)

            try:
                progress_bar = st.progress(0)
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

                        # write to back up csv file.
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

                        # update progress bar
                        progress_bar.progress((i + 1) / len(filtered_corpus1))
            except:
                backup_file.close()
                st.write(
                    f"The programme failed, however all the completed refs for {file1_name} are saved in the backup folder.")
                raise
            st.success("Comparison completed!")

            # Create a dataframe of all matched comparisons.
            df = pd.DataFrame(data={f'{file1_name}_ref': text_1_ref,
                                    f'{file1_name}_sample': text_1_list,
                                    f'{file2_name}_ref': text_2_ref,
                                    f'{file2_name}_sample': text_2_list,
                                    'model_explanation': explanations,
                                    'confidence_score': confidence_scores,
                                    'similarity_score': similarity_scores
                                    }).sort_values(by=['similarity_score', 'confidence_score'], ascending=False)

            st.write("\nSorting output to get results.")
            # # partition dataframe based on aligned and partially aligned categories.
            main_output_df = df.sort_values(by=['similarity_score', 'confidence_score'], ascending=False).copy()
            main_output_df['model_criteria'] = main_output_df['similarity_score'].apply(lambda x: model_judgment_criteria(x))

            # Provide a list of references from corpus2 that was not found in corpus1.
            non_matched_series = pd.DataFrame(data={
                f"{file2_name}_no_matches_refs":
                    non_matched_refs
            })

            # output aligned and partial aligned text.
            output_file_name = f'{file1_name}_{file2_name}_{model}_{today}'
            output_path = f"data/output/{output_file_name}.xlsx"

            with pd.ExcelWriter(output_path) as writer:
                main_output_df.to_excel(writer, sheet_name="matches", index=False)
                non_matched_series.to_excel(writer, sheet_name="NA", index=False)
            st.write(f"\nOutput complete. Saved in {output_path}")
            t2 = (time() - t1) / 60
            st.write(f"Mapping finished. Process took {t2:.2f} minutes.")


if __name__ == '__main__':
    main()
