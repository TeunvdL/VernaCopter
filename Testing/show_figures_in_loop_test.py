import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

def generate_figure(input_value):
    # Generate figure based on input_value
    x = range(input_value)
    y = [i ** 2 for i in x]
    
    # Plot the figure
    ax.clear()
    ax.plot(x, y)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Figure for input: {}'.format(input_value))

def input_thread():
    while True:
        try:
            user_input = input("Enter a number (or 'q' to quit): ")
            if user_input.lower() == 'q':
                break
            else:
                input_value = int(user_input)
                threading.Thread(target=generate_figure, args=(input_value,)).start()
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")

# Set up Matplotlib figure and axis
fig, ax = plt.subplots()

# Run input thread
input_thread()

plt.show()
