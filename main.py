from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
import pandas as pd
from datetime import datetime
import re
import argparse
from utils.data_handler import FileHandler


parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str, default='gpt-3.5-turbo')

args = parser.parse_args()

sample = True

today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
model = CompareText.model = args.model
prompt = CompareText()

# open specified files and get regulatory text cols.
file_handler = FileHandler()
regulatory_ref1, regulation_text1, regulatory_ref2, regulation_text2 = file_handler.get_reg_texts_cols()
file1_name, file2_name = file_handler.get_files_names()


# keyword extraction block.




# Caparator block.
text_1_list = []
text_1_ref = []

text_2_list = []
text_2_ref = []

explanations = []
confidence_scores = []
similarity_scores = []

for i, text1 in enumerate(regulation_text1):
    for j, text2 in enumerate(regulation_text2):
        print(f"comparing {file1_name} policy {i+1} to {file2_name} policy {j+1}")
        comparison = prompt.compare_texts_prompt(text_1=text1, text_2=text2)
        dict_output = parse_stringified_json(comparison)
        explanations.append(dict_output['explanation'])
        confidence_scores.append(dict_output['confidence_score'])
        similarity_scores.append(dict_output['similarity_score'])
        text_1_list.append(text1)
        text_1_ref.append(regulatory_ref1[i])
        text_2_list.append(text2)
        text_2_ref.append(regulatory_ref2[j])

df = pd.DataFrame(data={f'{file1_name}_ref': text_1_ref,
                        f'{file1_name}_sample': text_1_list,
                        f'{file2_name}_ref': text_2_ref,
                        f'{file2_name}_sample': text_2_list,
                        'model_explanation': explanations,
                        'confidence_score': confidence_scores,
                        'similarity_score': similarity_scores
                        }).sort_values(by=['similarity_score', 'confidence_score'], ascending=False)
aligned_df = df[df['similarity_score'] <= 0.7].copy()

output_file_name = f'sample_output_{model}_{today}'
df.to_excel(f"data/output/{output_file_name}.xlsx")
aligned_df.to_excel(f"data/output/filtered_{output_file_name}.xlsx")
