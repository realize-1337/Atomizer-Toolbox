import pandas as pd
import numpy as np
from fractions import Fraction

# calculate areas for PDA
def PDA_Area(max=100):
    if max < 20: raise ValueError
    r_i = np.concatenate((np.arange(0, 22, 2), np.arange(25, max+5, 5)))
    delta_r = np.diff(r_i)
    areas = np.zeros_like(delta_r.astype(np.float32))

    for i in range(len(areas)):
        if r_i[i] == 0:
            areas[i] = np.pi * (delta_r[i]/2) ** 2 
        else:
            areas[i] = np.pi * abs((r_i[i] - 0.5*delta_r[i])**2 - (r_i[i] + 0.5*delta_r[i])**2) / 2
    
    df = pd.Series(areas[::-1])
    df.to_clipboard(decimal=',', header=False, index=False)

def inverseClip(dec=','):
    df = pd.read_clipboard(header=None, index_col=None)
    arr = df.to_numpy()[::-1]
    df = pd.DataFrame(arr)
    df.to_clipboard(decimal=dec, header=False, index=False)

def test():
    import numpy as np
    import matplotlib.pyplot as plt

    # Generate some example data
    num_points = 100
    radius = np.linspace(0, 1, num_points)
    theta = np.linspace(0, 2*np.pi, num_points)
    data = np.random.rand(num_points)  # Example data, replace this with your actual data

    # Create a meshgrid
    r, th = np.meshgrid(radius, theta)

    # Plot the annulus with smooth color gradient
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    c = ax.pcolormesh(th, r, np.tile(data, (num_points, 1)), cmap='viridis', alpha=0.75)

    # Add additional circles
    for r in [0.25, 0.5, 0.75]:
        ax.plot(theta, np.full_like(theta, r), color='black', linestyle='--')

    # Add a colorbar
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_label('Data Value')

    plt.show()

def float_to_fraction(x, max_denominator=100):
    return Fraction(x).limit_denominator(max_denominator)

if __name__ == '__main__':
    inverseClip('.')
    # Example usage
    # numbers = [1.78E-04, -0.90162, 0.119866667, -6.52947, -434.38169, 0.128335269, -498914.5024, -199763000]
    # for num in numbers:
    #     fraction = float_to_fraction(num)
    #     print(fraction)  # Output: 3/4
    # pass
