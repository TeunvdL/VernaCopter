"""
This module provides functionality to transform a user-defined natural language specification
into a linear temporal logic (LTL)-specification using ChatGPT. The main function is `transform_to_ltl`, which
takes a natural language string as input and returns the corresponding LTL formula as a string.
"""

from openai import OpenAI

class NLToLTL:
    def __init__(self):
        self.client = OpenAI()

    def generate_ltl(self, init_messages, user_input, model="gpt-3.5-turbo"):
        """
        Generates an LTL specification from a given natural language input.

        Parameters:
        - init_messages (list of str): The initial messages to be sent to ChatGPT.
        - user_input (str): The natural language input.

        Returns:
        - str: The corresponding LTL specification.
        """

        messages = []

        messages.append(init_messages)
                
        messages.append(user_input)

        completion = self.client.chat.completions.create(
        model=model,
        messages=messages,
        )     

        return completion.choices[0].message.content