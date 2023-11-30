import matplotlib.pyplot as plt
import numpy as np


data = np.linspace(0,1,100)
plt.ion()
plt.ylim(0,1500)
i = 0
while i < 500:
    
    lines = plt.plot(i*np.exp(data), c="b")	# plot it
    plt.pause(0.002)
    lines.pop(0).remove()
    i += 1

plt.ioff()    