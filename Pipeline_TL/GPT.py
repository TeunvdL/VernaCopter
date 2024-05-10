from openai import OpenAI

class GPT:
    """
    Class for ChatGPT interaction.
    
    """
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI()
        self.model = model

    def chatcompletion(self, messages, temperature = 0.3):
        """
        ChatGPT interaction.

        Parameters
        ----------
        prompt : list of dict
            Prompt for ChatGPT.

        Returns
        -------
        str
            Response from ChatGPT.
        """

        completion = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=temperature
        )     

        return completion.choices[0].message.content