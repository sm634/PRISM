from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
import pandas as pd
from datetime import datetime
import re


today = re.sub('\.+', '', str(datetime.today())).replace(':', '-').replace(' ', '_')
model = CompareText.model = 'gpt-3.5-turbo'
prompt = CompareText()

dora_regulation_text = pd.read_excel('data/input/dora_regulation.xlsx', sheet_name=0)
dora_regulatory_ref = dora_regulation_text.columns[0]
dora_regulatory_col = dora_regulation_text.columns[1]
dora_regulation_text[dora_regulatory_col] = dora_regulation_text[
    dora_regulatory_col].apply(lambda x: x.replace('\n', ''))

iosco_regulation_text = pd.read_excel('data/input/iosco_regulation.xlsx', sheet_name=0)
iosco_regulatory_ref = iosco_regulation_text.columns[0]
iosco_regulatory_col = iosco_regulation_text.columns[1]
iosco_regulation_text[iosco_regulatory_col] = iosco_regulation_text[
    iosco_regulatory_col].apply(lambda x: x.replace('\n', ''))


dora_sample = dora_regulation_text.sample(1)
dora_refs = dora_sample[dora_regulatory_ref].to_list()
dora_text = dora_sample[dora_regulatory_col].to_list()


# first test
iosco_sample = iosco_regulation_text.sample(n=10, random_state=1)
iosco_refs = iosco_sample[iosco_regulatory_ref].to_list()
iosco_text = iosco_sample[iosco_regulatory_col].to_list()

text_1_list = []
text_1_ref = []

text_2_list = []
text_2_ref = []

explanations = []
confidence_scores = []
similarity_scores = []

for i, text1 in enumerate(dora_text):
    for j, text2 in enumerate(iosco_text):
        print(f"comparing dora regulation {i} to iosco regulation {j}")
        comparison = prompt.compare_texts_prompt(text_1=text1, text_2=text2)
        dict_output = parse_stringified_json(comparison)
        explanations.append(dict_output['explanation'])
        confidence_scores.append(dict_output['confidence_score'])
        similarity_scores.append(dict_output['similarity_score'])
        text_1_list.append(text1)
        text_1_ref.append(dora_refs[i])
        text_2_list.append(text2)
        text_2_ref.append(iosco_refs[j])

df = pd.DataFrame(data={'dora_ref': text_1_ref,
                        'dora_sample': text_1_list,
                        'iosco_ref': text_2_ref,
                        'iosco_sample': text_2_list,
                        'explanation': explanations,
                        'confidence_score': confidence_scores,
                        'similarity_score': similarity_scores
                        }).sort_values(by=['similarity_score', 'confidence_score'], ascending=False)
# filtered_df = df[df['similarity_score'] >= 0.6].copy()

output_file_name = f'sample_output_{model}_{today}'
df.to_excel(f"data/output/{output_file_name}.xlsx")
# filtered_df.to_excel(f"data/output/{output_file_name}.xlsx")
