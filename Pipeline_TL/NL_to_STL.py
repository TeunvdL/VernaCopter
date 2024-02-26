from GPT import *
from STL_to_path import *
import os
import time

class NL_to_STL:
    """
    Class for converting natural language to STL formula.

    """

    def __init__(self, objects, T_max, dt, print_instructions=False):
        self.objects = objects
        self.T_max = T_max
        self.dt = dt
        self.print_instructions = print_instructions

    def generate_specs(self):
        response = self.gpt_conversation()
        specs = self.extract_specs(response)
        return specs

    def gpt_conversation(self, max_inputs=5):
        gpt = GPT()
        instructions_template = self.load_chatgpt_instructions()
        instructions = self.insert_instruction_variables(instructions_template)
        if self.print_instructions:
            print("Instructions: ", instructions, "\n", "______________________________")
        messages = [{"role": "system", "content": instructions}]   

        print("Please specify the task. Type 'quit' to exit conversation.")
        for i in range(max_inputs):
            user_input = input("User: ")

            if user_input.lower() == 'quit':
                print("Exited conversation")
                break

            messages.append({"role": "user", "content": user_input})
            response = gpt.chatcompletion(messages)
            messages.append({"role": "assistant", "content": response})

            # check if < or > symbol is present in the response and exit conversation if detected
            if '<' in response:
                print("The final specification was generated. Exiting conversation.")
                break

            print("Assistant:", response)

            # pause for a short time such that the response is printed properly
            time.sleep(0.5)
        
        final_response = messages[-1]["content"]
        return final_response
    
    def load_chatgpt_instructions(self):
        path = os.path.dirname(os.path.abspath(__file__))
        instructions_file = open(path + '/ChatGPT_instructions.txt', 'r')
        instructions = instructions_file.read()
        return instructions
    
    def insert_instruction_variables(self, instructions):
        instructions = instructions.replace("OBJECTS", str(self.objects))
        instructions = instructions.replace("T_MAX", str(self.T_max))
        return instructions
    
    def extract_specs(self, response):
        specs = []
        start = 0
        while True:
            start = response.find("<", start)
            if start == -1:
                break
            end = response.find(">", start)
            specs.append(response[start+1:end])
            start = end
        return specs