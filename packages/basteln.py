import pandas as pd
import numpy as np

# calculate areas for PDA
if __name__ == '__main__':
    r_i = np.concatenate((np.arange(0, 22, 2), np.arange(25, 95, 5)))
    delta_r = np.diff(r_i)
    areas = np.zeros_like(delta_r.astype(np.float32))

    for i in range(len(areas)):
        if r_i[i] == 0:
            areas[i] = np.pi * (delta_r[i]/2) ** 2 
        else:
            areas[i] = np.pi * abs((r_i[i] - 0.5*delta_r[i])**2 - (r_i[i] + 0.5*delta_r[i])**2) / 2
    
    df = pd.Series(areas[::-1])
    df.to_clipboard(decimal=',', header=False, index=False)
    pass
