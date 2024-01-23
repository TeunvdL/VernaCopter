from openai import OpenAI

class GPT:
    """
    ChatGPT_move_to class for ChatGPT interaction.
    
    """
    def __init__(self):
        self.client = OpenAI()

    def chatcompletion(self, init_messages, user_input, model="gpt-3.5-turbo"):
        """
        ChatGPT interaction.

        Parameters
        ----------
        init_messages : list of dict
            Initial messages for ChatGPT.
        user_input : list of dict
            User input to get target position.
        model : str, optional
            ChatGPT model. The default is "gpt-3.5-turbo".

        Returns
        -------
        str
            Target position.
        """

        messages = []

        for init_message in init_messages:
            messages.append(init_message)

        for input in user_input:        
            messages.append(input)

        completion = self.client.chat.completions.create(
        model=model,
        messages=messages,
        )     

        return completion.choices[0].message.content