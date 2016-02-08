import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib



def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    #print seq
    #print list(seq)
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        #print i, item
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)


c = mcolors.ColorConverter().to_rgb
rvb = make_colormap(
    [c('red'), c('violet'), 0.50, c('violet'), c('blue')])

def find_color_value(x):
    min_val = -100
    max_val = 100

    my_cmap = cm.get_cmap(rvb) # or any other one
    norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

    x_i = x
    color_i = my_cmap(norm(x_i)) # returns an rgba value
    return(color_i)


#test1,test2,test3,test4= find_color_value(10)
#print test1*255
#print test2*255
#print test3*255


