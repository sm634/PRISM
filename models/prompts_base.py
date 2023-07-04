

class Prompts:

    def __init__(self, model, max_tokens, temperature):
        """
        Instantiate the model and its parameters.
        :param model: the model you want to use, e.g. gpt-3.5, text-davinci-003.
        :param max_tokens: the maximum number of tokens to accept for the model's prompt space.
        :param temperature: How deterministic the model's output should be. Range [0, 1]. Higher temperature means less
        deterministic.
        """
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model

