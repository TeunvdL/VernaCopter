from GPT import *
from STL_to_path import *
import os
import time
from logger import *

class NL_to_STL:
    """
    Class for converting natural language to STL formula.

    """

    def __init__(self, objects, N, dt, print_instructions=False):
        self.objects = objects
        self.dt = dt
        self.N = N
        self.print_instructions = print_instructions
        self.gpt = GPT()

    def get_specs(self, messages):
        print("Extracting the specification...")
        response = messages[-1]['content']
        spec = self.extract_spec(response)
        return spec

    def gpt_conversation(self, max_inputs=10, previous_messages=[], processing_feedback=False, status="active"):
        
        if not previous_messages:
            instructions_template = self.load_chatgpt_instructions('ChatGPT_instructions.txt')
            instructions = self.insert_instruction_variables(instructions_template)
            if self.print_instructions:
                print("Instructions: ", instructions, "\n", "______________________________")
            messages = [{"role": "system", "content": instructions}]
        else:
            messages = previous_messages   

        if processing_feedback:
            print(logger.color_text("Processing feedback...", 'yellow'))
            response = self.gpt.chatcompletion(messages)
            messages.append({"role": "assistant", "content": response})
            print(logger.color_text("Assistant:", 'cyan'), response)
        else:
            print("Please specify the task. Type 'quit' to exit conversation and generate the final trajectory.")
            for _ in range(max_inputs):
                user_input = input(logger.color_text("User: ", 'orange'))

                if user_input.lower() == 'quit':
                    print(logger.color_text("Exited conversation", 'yellow'))
                    status = "exited"
                    break

                messages.append({"role": "user", "content": user_input})
                response = self.gpt.chatcompletion(messages)
                messages.append({"role": "assistant", "content": response})
                print(logger.color_text("Assistant:", 'cyan'), response)

                # check if < or > symbol is present in the response and exit conversation if detected
                if '<' in response:
                    print("The specification was generated.")
                    break
    
        return messages, status
    
    def gpt_syntax_checker(self, spec):
        instructions_template = self.load_chatgpt_instructions('syntax_checker_instructions.txt')
        instructions = self.insert_instruction_variables(instructions_template)
        messages = [{"role": "system", "content": instructions}]
        messages.append({"role": "user", "content": f'Original specification: {spec}'})
        response = self.gpt.chatcompletion(messages)
        print(logger.color_text("Syntax checker:", 'purple'), response)
        new_spec = self.extract_spec(response)
        return new_spec
    
    def load_chatgpt_instructions(self, filename):
        path = os.path.dirname(os.path.abspath(__file__))
        instructions_file = open(path + '/' + filename, 'r')
        instructions = instructions_file.read()
        return instructions
    
    def insert_instruction_variables(self, instructions):
        try:
            instructions = instructions.replace("OBJECTS", str(self.objects))
        except:
            pass
        try:
            instructions = instructions.replace("T_MAX", str(self.N))
        except:
            pass
        return instructions
    
    def extract_spec(self, response):
        start = 0
        while True:
            start = response.find("<", start)
            if start == -1:
                break
            end = response.find(">", start)
            spec = response[start+1:end]
            start = end + 1
        return spec