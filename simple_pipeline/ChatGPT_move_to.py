from openai import OpenAI

class ChatGPT_move_to:
    def __init__(self):
        self.client = OpenAI()

    def chatcompletion(self, init_messages, user_input, model="gpt-3.5-turbo"):

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