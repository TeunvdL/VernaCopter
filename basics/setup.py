from .scenarios import *

class Default_parameters:
    def __init__(self, scenario_name="reach_avoid"):
        # Parameters
        self.max_acc = 10                            # maximum acceleration in m/s^2
        self.max_speed = 0.5                         # maximum speed in m/s 
        self.dt = 0.7                                # time step in seconds
        self.scenario_name = scenario_name           # scenario: "reach_avoid" or "treasure_hunt"
        self.GPT_model = "gpt-3.5-turbo"             # GPT version: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", etc.

        # System flags
        self.syntax_checker_enabled = False          # Enable syntax check for the trajectory
        self.spec_checker_enabled = False            # Enable specification check
        self.dynamicless_check_enabled = False       # Enable dynamicless specification check
        self.manual_spec_check_enabled = True        # Enable manual specification check
        self.manual_trajectory_check_enabled = True  # Enable manual trajectory check

        # Visualization flags
        self.animate_final_trajectory = True         # Animate the final trajectory
        self.save_animation = False                  # Save the final trajectory animation
        self.show_map = False                        # Show a map of the scenario at the start of the program

        # Logging flags
        self.solver_verbose = False                  # Enable solver verbose
        self.print_ChatGPT_instructions = False      # Print ChatGPT instructions

        # Loop iteration limits
        self.syntax_check_limit = 5                  # Maximum number of syntax check iterations
        self.spec_check_limit = 5                    # Maximum number of specification check iterations

        self.instructions_file = 'ChatGPT_instructions.txt'
        
        scenario = Scenarios(self.scenario_name)
        self.T_initial = scenario.T_initial          # Initial time

        self.save_results = False                    # Save results to a file

        self.automated_user = False                  # Automated user flag
        self.automated_user_input = ""               # Automated user input

        self.STL_included = True                     # Include STL in the system


class One_shot_parameters:
    def __init__(self, scenario_name="reach_avoid"):
        # Parameters
        self.max_acc = 10                            # maximum acceleration in m/s^2
        self.max_speed = 0.5                         # maximum speed in m/s 
        self.dt = 0.7                                # time step in seconds
        self.scenario_name = scenario_name           # scenario: "reach_avoid" or "treasure_hunt"
        self.GPT_model = "gpt-3.5-turbo"             # GPT version: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", etc.

        # System flags
        self.syntax_checker_enabled = True           # Enable syntax check for the trajectory
        self.spec_checker_enabled = True             # Enable specification check
        self.dynamicless_check_enabled = False       # Enable dynamicless specification check
        self.manual_spec_check_enabled = False       # Enable manual specification check
        self.manual_trajectory_check_enabled = False # Enable manual trajectory check

        # Visualization flags
        self.animate_final_trajectory = False        # Animate the final trajectory
        self.save_animation = False                  # Save the final trajectory animation
        self.show_map = False                        # Show a map of the scenario at the start of the program

        # Logging flags
        self.solver_verbose = False                  # Enable solver verbose
        self.print_ChatGPT_instructions = False      # Print ChatGPT instructions

        # Loop iteration limits
        self.syntax_check_limit = 5                  # Maximum number of syntax check iterations
        self.spec_check_limit = 5                    # Maximum number of specification check iterations

        self.instructions_file = 'one_shot_ChatGPT_instructions.txt'
        
        scenario = Scenarios(self.scenario_name)
        self.T_initial = scenario.T_initial          # Initial time

        self.save_results = True                     # Save results to a file

        self.automated_user = True                   # Automated user flag
        self.automated_user_input = "Reach the goal while avoiding the obstacles."

        self.STL_included = True                     # Include STL in the system


class non_STL_default_parameters:
    def __init__(self, scenario_name="reach_avoid"):
        # Parameters
        self.max_acc = 10                            # maximum acceleration in m/s^2
        self.max_speed = 0.5                         # maximum speed in m/s 
        self.dt = 0.7                                # time step in seconds
        self.scenario_name = scenario_name           # scenario: "reach_avoid" or "treasure_hunt"
        self.GPT_model = "gpt-3.5-turbo"             # GPT version: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", etc.

        # System flags
        self.syntax_checker_enabled = True           # Enable syntax check for the trajectory
        self.spec_checker_enabled = True             # Enable specification check
        self.dynamicless_check_enabled = False       # Enable dynamicless specification check
        self.manual_spec_check_enabled = False       # Enable manual specification check
        self.manual_trajectory_check_enabled = False # Enable manual trajectory check

        # Visualization flags
        self.animate_final_trajectory = False        # Animate the final trajectory
        self.save_animation = False                  # Save the final trajectory animation
        self.show_map = False                        # Show a map of the scenario at the start of the program

        # Logging flags
        self.solver_verbose = False                  # Enable solver verbose
        self.print_ChatGPT_instructions = False      # Print ChatGPT instructions

        # Loop iteration limits
        self.syntax_check_limit = 5                  # Maximum number of syntax check iterations
        self.spec_check_limit = 5                    # Maximum number of specification check iterations

        self.instructions_file = 'non_STL_ChatGPT_instructions.txt'
        
        scenario = Scenarios(self.scenario_name)
        self.T_initial = scenario.T_initial          # Initial time

        self.save_results = True                     # Save results to a file

        self.automated_user = True                   # Automated user flag
        self.automated_user_input = "Reach the goal while avoiding the obstacles."

        self.STL_included = True                     # Include STL in the system        


class non_STL_one_shot_parameters:
    def __init__(self, scenario_name="reach_avoid"):
        # Parameters
        self.max_acc = 10                            # maximum acceleration in m/s^2
        self.max_speed = 0.5                         # maximum speed in m/s 
        self.dt = 0.7                                # time step in seconds
        self.scenario_name = scenario_name           # scenario: "reach_avoid" or "treasure_hunt"
        self.GPT_model = "gpt-3.5-turbo"             # GPT version: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", etc.

        # System flags
        self.syntax_checker_enabled = True           # Enable syntax check for the trajectory
        self.spec_checker_enabled = True             # Enable specification check
        self.dynamicless_check_enabled = False       # Enable dynamicless specification check
        self.manual_spec_check_enabled = False       # Enable manual specification check
        self.manual_trajectory_check_enabled = False # Enable manual trajectory check

        # Visualization flags
        self.animate_final_trajectory = False        # Animate the final trajectory
        self.save_animation = False                  # Save the final trajectory animation
        self.show_map = False                        # Show a map of the scenario at the start of the program

        # Logging flags
        self.solver_verbose = False                  # Enable solver verbose
        self.print_ChatGPT_instructions = False      # Print ChatGPT instructions

        # Loop iteration limits
        self.syntax_check_limit = 5                  # Maximum number of syntax check iterations
        self.spec_check_limit = 5                    # Maximum number of specification check iterations

        self.instructions_file = 'non_STL_ChatGPT_instructions.txt'
        
        scenario = Scenarios(self.scenario_name)
        self.T_initial = scenario.T_initial          # Initial time

        self.save_results = True                     # Save results to a file

        self.automated_user = True                   # Automated user flag
        self.automated_user_input = "Reach the goal while avoiding the obstacles."

        self.STL_included = True                     # Include STL in the system        