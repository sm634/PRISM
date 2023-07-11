from decouple import config
import openai
from openai.error import RateLimitError
import backoff
from models.prompts_base import Prompts
import json

openai.api_key = config('OPENAI_API_KEY')


class PromptsInvoice(Prompts):

    def __init__(self):
        Prompts.__init__(self, model="text-davinci-003", max_tokens=1000, temperature=0)

    @staticmethod
    def __extract_invoice_prompt(data_fields, prompt_text, invoice_text):
        return f"""your job is to extract the values for the following data fields {data_fields}.
                
                {prompt_text}
                
                "{invoice_text}"
            """

    @backoff.on_exception(backoff.expo, RateLimitError, max_time=300)
    def chat_completions_with_backoff(self, data_fields, prompt_text, invoice_text, retry=True):
        while retry:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful reading assistant who will be provided text"
                                                      "from an invoice. You will be asked to extract values for a set of"
                                                      "data fields from that invoice text and return it as a response. The text"
                                                      "you will be provided are not always easy to read, but you should make"
                                                      "the best guess based on the characteristics and examples provided in the"
                                                      "prompts for you."},
                        {"role": "user", "content": self.__extract_invoice_prompt(data_fields=data_fields,
                                                                                  prompt_text=prompt_text,
                                                                                  invoice_text=invoice_text)}
                    ],
                    temperature=self.temperature,
                    n=1,
                    max_tokens=self.max_tokens
                )
                return response['choices'][0]['message']['content']
            except RateLimitError:
                print(f"Requests to the model are at maximum capacity, cooling off before retrying the requests"
                      f" using exponential backoff.")
            except openai.error.APIError as e:
                print(f"The request ran into an OpenAI server issue. Retrying the request again.")

    @backoff.on_exception(backoff.expo, RateLimitError, max_time=300)
    def completions_with_backoff(self, data_fields, prompt_text, invoice_text, retry=True):
        # try - except clause to handle bad gateway problems.
        while retry:
            try:
                response = openai.Completion.create(
                    engine=self.model,
                    prompt=self.__extract_invoice_prompt(data_fields=data_fields,
                                                         prompt_text=prompt_text,
                                                         invoice_text=invoice_text),
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].text
            except RateLimitError:
                print(f"Requests to the model are at maximum capacity, cooling off before retrying the requests"
                      f" using exponential backoff.")
            except openai.error.APIError:
                print(f"The request ran into an OpenAI server issue. Retrying the request again.")

    def extract_invoice_info(self, data_fields, prompt_text, invoice_text, file_index):
        """
        :param file_index: For output, to provide reference for the file being processed by model.
        :param invoice_text: The text from invoice as input to extract information from.
        :param data_fields: values for data fields to extract
        :return: a string, comma separated with all the values we require.
        """

        extracted_values = ''

        if self.model == 'text-davinci-003':
            extracted_values = self.completions_with_backoff(data_fields, prompt_text, invoice_text)
            print(f"Extracting data field values from document {file_index}")

        elif self.model == 'gpt-3.5-turbo' or self.model == 'gpt-3.5-turbo-0301':

            extracted_values = self.chat_completions_with_backoff(data_fields, prompt_text, invoice_text)
            print(f"Extracting data field values from document {file_index}")

        return extracted_values


class CompareText(Prompts):
    def __init__(self):
        Prompts.__init__(self, model="gpt-3.5-turbo", max_tokens=1000, temperature=0)

    @staticmethod
    def __compare_policies(text_1, text_2):
        """
        Compares two blocks of texts, explains if they are similar or not, provides a similiarity score (range
         of [0, 1]) and a confidence score (range of [0, 1]) showing how confident the judgment is.
        :param text_1: The first block of text to compare.
        :param text_2: The second block of text to compare.
        :return: A json that looks like {
                                        "explanation": explanation_value,
                                        "similarity_score": 0.5,
                                        "confidence_score": 0.9
                                         }
        """

        return f"""Compare text 1 and text 2 below of legal policies. Summarize text 1 and text 2. 
        Explain if they are similar or different and give reasons on why. Return a json output with a key value 
        of the explanation, a key-value pair of similarity score in range [0,1] between the two texts, 
        and another key-value pair of confidence score in range [0,1]. Make sure the similarity and confidence scores 
        take into account similarity between text 1 and text 2 on all aspects.
        
        Example: 
        
        "explanation": "They are similar because they are both focused on ... but the differences are ...", 
        "similarity_score": 0.5,
        "confidence_score": 0.5

        text 1: {text_1}  
        
        text 2: {text_2}
        
        """

    @staticmethod
    def compare_texts(text_1, text_2):
        text_info = {
            "text_1": text_1,
            "text_2": text_2,
        }
        return json.dumps(text_info)

    @backoff.on_exception(backoff.expo, RateLimitError, max_time=300)
    def chat_completions_with_backoff(self, text_1, text_2, retry=True):
        while retry:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful policy analyst. Your job is to compare blocks"
                                                      "of text and assess how similar or different they are and return"
                                                      "a json with the explanation, scores to indicate their similarity"
                                                      "and your confidence in making that judgment."},
                        {"role": "user", "content": self.__compare_policies(text_1, text_2)}
                    ],
                    temperature=self.temperature,
                    n=1,
                    max_tokens=self.max_tokens
                )
                return response['choices'][0]['message']['content']
            except RateLimitError:
                print(f"Requests to the model are at maximum capacity, cooling off before retrying the requests"
                      f" using exponential backoff.")
            except openai.error.APIError:
                print(f"The request ran into an OpenAI server issue. Retrying the request again.")
            except openai.error.ServiceUnavailableError as e:
                print(f"{e}. Trying again with exponential backoff.")

    @backoff.on_exception(backoff.expo, RateLimitError, max_time=300)
    def completions_with_backoff(self, text_1, text_2, retry=True):
        # try - except clause to handle bad gateway problems.
        while retry:
            try:
                response = openai.Completion.create(
                    engine=self.model,
                    prompt=self.__compare_policies(text_1, text_2),
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].text

            except RateLimitError:
                print(f"Requests to the model are at maximum capacity, cooling off before retrying the requests"
                      f" using exponential backoff.")
            except openai.error.APIError:
                print(f"The request ran into an OpenAI server issue. Retrying the request again.")
            except openai.error.ServiceUnavailableError as e:
                print(f"{e}. Trying again with exponential backoff.")

    def compare_policies_prompt(self, text_1, text_2):
        """
        :param text_1: The first block of text to compare.
        :param text_2: The second block of text to compare.
        :return: A json that looks like {
                                        "explanation": explanation_value,
                                        "similarity_score": 0.5,
                                        "confidence_score": 0.9
                                         }
        """

        extracted_values = ''

        if self.model == 'text-davinci-003':
            extracted_values = self.completions_with_backoff(text_1, text_2)

        elif self.model == 'gpt-3.5-turbo' or self.model == 'gpt-3.5-turbo-0301':

            extracted_values = self.chat_completions_with_backoff(text_1, text_2)

        return extracted_values
