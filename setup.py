class setup_parameters:
    def __init__(self):
        # Parameters
        self.max_acc = 10                            # maximum acceleration in m/s^2
        self.max_speed = 0.5                         # maximum speed in m/s 
        self.dt = 0.7                                # time step in seconds
        self.scenario_name = "reach_avoid"           # scenario: "reach_avoid", "narrow_maze", or "treasure_hunt"
        self.GPT_model = "gpt-3.5-turbo"             # GPT version: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", etc.

        # System flags
        self.syntax_checker_enabled = False          # Enable syntax check for the trajectory
        self.spec_checker_enabled = False            # Enable specification check
        self.dynamicless_check_enabled = False       # Enable dynamicless specification check
        self.manual_spec_check_enabled = True        # Enable manual specification check
        self.manual_trajectory_check_enabled = True  # Enable manual trajectory check

        # Visualization flags
        self.animate_final_trajectory = True         # Animate the final trajectory
        self.show_map = False                        # Show a map of the scenario at the start of the program

        # Logging flags
        self.solver_verbose = False                  # Enable solver verbose
        self.print_ChatGPT_instructions = False      # Print ChatGPT instructions

        # Loop iteration limits
        self.syntax_check_limit = 5                  # Maximum number of syntax check iterations
        self.spec_check_limit = 5                    # Maximum number of specification check iterations