import numpy as np
import matplotlib.pyplot as plt

import os

def get(a = 0.5, b = 1, outlierProb = 0.1):
    np.random.seed(10)

    e = np.random.normal(0, 1, 50)

    x = np.arange(1, 51)
    y = a * x + b + e

    indices = []

    p = np.random.rand(50)
    for i in range(50):
        if p[i] <= outlierProb:
            y[i] = -0.25 * x[i] + 40 + e[i]
        else:
            indices.append(i)

    return x, y, x[indices], y[indices]

# if not used as a module, plot the dataset
if __name__ == "__main__":
    x, y = get(0.5, 1, 0.2)[1, 2]

    plt.rcParams['figure.figsize'] = 10, 7

    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['axes.linewidth'] = 2
    
    plt.rcParams['font.size'] = 20
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['text.usetex'] = 'true'
   
    plt.plot(x, y, 'x')

    path = os.path.expanduser('~/Documents/Projects/vhartman.github.io/images/robust/data.png')
    plt.savefig(path, bbox_inches='tight')

