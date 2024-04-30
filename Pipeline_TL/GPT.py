from openai import OpenAI

class GPT:
    """
    Class for ChatGPT interaction.
    
    """
    def __init__(self):
        self.client = OpenAI()

    def chatcompletion(self, messages, model="gpt-3.5-turbo", temperature = 0.3):
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
        model=model,
        messages=messages,
        temperature=temperature
        )     

        return completion.choices[0].message.content