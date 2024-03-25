import tkinter as tk
from tkinter import simpledialog
import sys

# Function to get user input in a separate window
def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Input", "Enter your input:")
    return user_input

# Function to print colored text
def print_colored_text(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(colors[color] + text + colors['reset'])

# Main function
def main():
    # Get user input in a separate window
    user_input = get_user_input()
    print("User input:", user_input)

    # Print colored text
    print_colored_text("This is red text", 'red')
    print_colored_text("This is green text", 'green')
    print_colored_text("This is blue text", 'blue')

if __name__ == "__main__":
    main()
