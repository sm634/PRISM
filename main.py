from models.prompts import CompareText
from utils.parse_output import parse_stringified_json
import pandas as pd

model = CompareText.model = 'gpt-3.5-turbo'
prompt = CompareText()

t1 = """
Competent authorities may, as a measure of last resort, following the notification and, if appropriate, 
the consultation as set out in paragraph 4 and 5 of this Article, in accordance with Article 50, 
take a decision requiring financial entities to temporarily suspend, either in part or completely, 
the use or deployment of a service provided by the critical ICT third-party service provider until the risks identified 
in the recommendations addressed to critical ICT third-party service providers have been addressed. Where necessary, 
they may require financial entities to terminate, in part or completely, the relevant contractual arrangements 
concluded with the critical ICT third-party service providers.
""".replace("\n", '')

t2 = """
While IOSCO states that entitties 'may' consider appointing a resource to oversee outsourcing arrangements, 
DORA focuses on entity's obligation on designating a member of senior management to oversee and monitor third party 
arrangements as well as managing risk exposure and relevant documentation (ICTRM 5.3). 
Additionally, DORA mentions members of the management body to actively keep up to date with sufficient knowledge, 
skills and training to effectively manage ICT risk (ICTRM 5.4)
""".replace("\n", '')

output_dict = {"text_1": t1,
               "text_2": t2}

output = prompt.compare_texts_prompt(text_1=t1, text_2=t2)
output = parse_stringified_json(output)
output_dict.update(output)
df_output = pd.DataFrame(output_dict, index=[0])

print(df_output)
breakpoint()
