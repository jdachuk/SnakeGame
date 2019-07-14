"""
author: edacjos
created: 7/14/19
"""

import matplotlib.pyplot as plt
import pandas as pd
from itertools import count
from matplotlib.animation import FuncAnimation
from support import Const


def animate(i):
    names = ['generation_id', 'generation_size', 'total_fitness', 'top_fitness']
    data = pd.read_csv(f'data\\V_{Const.VERSION}\\info\\progress.csv', names=names)
    x = data['generation_id']
    y1 = data['total_fitness'] / data['generation_size']
    y2 = data['top_fitness']

    plt.cla()

    plt.plot(x, y1, label='Average fitness')
    plt.plot(x, y2, label='Top fitness')

    plt.legend(loc='upper left')
    plt.tight_layout()


index = count()

ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
