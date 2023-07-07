from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
import pandas as pd
from datetime import datetime
import re
import argparse


parser = argparse.ArgumentParser()

sample = True

today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
model = CompareText.model = 'gpt-3.5-turbo'
prompt = CompareText()

# take input files
with open('reference_docs/input_files.txt', 'r') as f:
    files = f.read()
    files_list = files.split(',')
    f.close()

file1 = files_list[0]
file2 = files_list[1]

file1_name = file1.replace('.xlsx', '')
file2_name = file2.replace('.xlsx', '')

dora_regulation_text = pd.read_excel(f'data/input/{file1}', sheet_name=0)
dora_regulatory_ref = dora_regulation_text.columns[0]
dora_regulatory_col = dora_regulation_text.columns[1]
dora_regulation_text[dora_regulatory_col] = dora_regulation_text[
    dora_regulatory_col].apply(lambda x: x.replace('\n', ''))

iosco_regulation_text = pd.read_excel(f'data/input/{file2}', sheet_name=0)
iosco_regulatory_ref = iosco_regulation_text.columns[0]
iosco_regulatory_col = iosco_regulation_text.columns[1]
iosco_regulation_text[iosco_regulatory_col] = iosco_regulation_text[
    iosco_regulatory_col].apply(lambda x: x.replace('\n', ''))

if sample:
    dora_sample = dora_regulation_text.sample(n=2, random_state=1)
    dora_refs = dora_sample[dora_regulatory_ref].to_list()
    dora_text = dora_sample[dora_regulatory_col].to_list()

    # first test
    iosco_sample = iosco_regulation_text.sample(n=4, random_state=1)
    iosco_refs = iosco_sample[iosco_regulatory_ref].to_list()
    iosco_text = iosco_sample[iosco_regulatory_col].to_list()
else:
    dora_refs = dora_regulation_text[dora_regulatory_ref].to_list()
    dora_text = dora_regulation_text[dora_regulatory_col].to_list()

    iosco_refs = iosco_regulation_text[iosco_regulatory_ref].to_list()
    iosco_text = iosco_regulation_text[iosco_regulatory_col].to_list()


text_1_list = []
text_1_ref = []

text_2_list = []
text_2_ref = []

explanations = []
confidence_scores = []
similarity_scores = []

for i, text1 in enumerate(dora_text):
    for j, text2 in enumerate(iosco_text):
        print(f"comparing {file1_name} policy {i+1} to {file2_name} policy {j+1}")
        comparison = prompt.compare_texts_prompt(text_1=text1, text_2=text2)
        dict_output = parse_stringified_json(comparison)
        explanations.append(dict_output['explanation'])
        confidence_scores.append(dict_output['confidence_score'])
        similarity_scores.append(dict_output['similarity_score'])
        text_1_list.append(text1)
        text_1_ref.append(dora_refs[i])
        text_2_list.append(text2)
        text_2_ref.append(iosco_refs[j])

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
