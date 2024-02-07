from GPT import *
from STL_to_path import *
import os

class NL_to_STL:
    """
    Class for converting natural language to STL formula.

    """

    def __init__(self, objects, T_max, dt):
        self.objects = objects
        self.T_max = T_max
        self.dt = dt
        self.functions = ["STL_formulas.inside_cuboid(object)",
                          "STL_formulas.outside_cuboid(object)",
                          "STL_formulas.inside_sphere(object)",
                          "STL_formulas.outside_sphere(object)",]
        self.STL_operators = ["&", "|"]
        self.STL_functions = ["eventually(T1, T2)", "always(T1, T2)"]

    
    def load_chatgpt_instructions(self):
        path = os.path.dirname(os.path.abspath(__file__))
        instructions_file = open(path + '/ChatGPT_instructions.txt', 'r')
        instructions = instructions_file.read()
        return instructions
    
    def insert_instruction_variables(self, instructions):
        instructions = instructions.replace("OBJECTS", str(self.objects))
        instructions = instructions.replace("FUNCTIONS", str(self.functions))
        instructions = instructions.replace("STL_OPERATORS", str(self.STL_operators))
        instructions = instructions.replace("STL_FUNCTIONS", str(self.STL_functions))
        instructions = instructions.replace("T_MAX", str(self.T_max))
        return instructions
    
    def get_gpt_response(self, user_input):
        gpt = GPT()
        instructions_template = self.load_chatgpt_instructions()
        instructions = self.insert_instruction_variables(instructions_template)
        init_messages = [{"role": "system", "content": instructions}]
        response = gpt.chatcompletion(init_messages, user_input)
        print("GPT response: ", response)
        return response

    def extract_STL_formula(self, user_input):
        objects = self.objects
        N_max = int(self.T_max/self.dt)
        response = self.get_gpt_response(user_input)
        start = response.find("<")
        end = response.find(">")
        STL_formula = response[start+1:end]
        print("Extracted STL formula: ", STL_formula)
        return eval(STL_formula)