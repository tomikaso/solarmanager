import matplotlib.pyplot as plt
import numpy as np

def plot_boiler(x, y, miny, maxy):
    fig = plt.figure(figsize=(8, 4), facecolor='aquamarine')
    ax = fig.add_subplot()
    ax.set_title('°C', loc='left', fontstyle='oblique', fontsize='medium')
    ax.plot(x, y, linewidth=2.0)
    ax.set(xlim=(0, len(x)), xticks=np.arange(1, len(x), int((len(x)+10)/10)),
       ylim=(miny, maxy), yticks=np.arange(miny, maxy, 2))
    plt.ylabel('temperature')
    plt.title('Boiler temperature')
    plt.savefig("/var/www/html/boiltemp.png", dpi=100)
    plt.close()
#   plt.show()

def plot_energy(x, y1, y2, y3, y4, y5, y6, miny, maxy):
    fig = plt.figure(figsize=(8, 4), facecolor='lightskyblue')
    colors = ['orange', 'green', 'blue', 'red', 'brown', 'purple']
    ax = fig.add_subplot()
    plt.gca().set_prop_cycle(color=colors)
    ax.set_title('Watt', loc='left', fontstyle='oblique', fontsize='medium')
    ax.plot(x, y1, linewidth=2.0, label='load')
    ax.plot(x, y2, linewidth=2.0, label='solar')
    ax.plot(x, y3, linewidth=2.0, label='theoretical')
    ax.plot(x, y4, linewidth=2.0, label='boiler state')
    ax.plot(x, y5, linewidth=2.0, label='plug state')
    ax.plot(x, y6, linewidth=2.0, label='hp state')
    ax.set(xlim=(0, len(x)), xticks=np.arange(1, len(x), int((len(x)+10)/10)),
           ylim=(miny, maxy), yticks=np.arange(miny, maxy, 1000))
    plt.ylabel('power')
    plt.title('Electric power')
    plt.legend()
    plt.savefig("/var/www/html/electricpower.png", dpi=100)
    plt.close()
#   plt.show()

def plot_house(x, y, miny, maxy):
    fig = plt.figure(figsize=(8, 4), facecolor='mediumspringgreen')
    ax = fig.add_subplot()
    ax.set_title('°C', loc='left', fontstyle='oblique', fontsize='medium')
    ax.plot(x, y, linewidth=2.0)
    ax.set(xlim=(0, len(x)), xticks=np.arange(1, len(x), int((len(x)+10)/10)),
           ylim=(miny, maxy), yticks=np.arange(miny, maxy, 1))
    plt.ylabel('temperature')
    plt.title('Living room temperature')
    plt.savefig("/var/www/html/housetemp.png", dpi=100)
    plt.close()