import os
import sys
import json
from numpy import fft
from operator import add
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path

def myplot(data):
    fig, ax = plt.subplots()

    # histogram our data with numpy
    n, bins = np.histogram(data, 50)

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n


    # we need a (numrects x numsides x 2) numpy array for the path helper
    # function to build a compound path
    XY = np.array([[left,left,right,right], [bottom,top,top,bottom]]).T

    # get the Path object
    barpath = path.Path.make_compound_path_from_polys(XY)

    # make a patch out of it
    patch = patches.PathPatch(barpath, facecolor='blue', edgecolor='gray', alpha=0.8)
    ax.add_patch(patch)

    # update the view limits
    ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())

    plt.show()

def main():
    train_file = open(sys.argv[1]).read()
    train_data = json.loads(train_file)
    # Collect instances of P and Q
    p_feat = []
    q_feat = []
    for sample in train_data:
        if sample['key']=='p':
            p_feat.append(sample)
        elif sample['key']=='q':
            q_feat.append(sample)

    # Conducting fft 
    avg_dist_p = dict()
    p_counter = 0
    for each_p in p_feat:
        p_counter+=1
        if len(avg_dist_p)==0:
            for each_key in each_p.keys():
                if each_key != 'key':
                    avg_dist_p.update({each_key:fft.fft([float(x) for x in each_p[each_key].split(',')])})
        else:
            for each_key in each_p.keys():
                if each_key != 'key':
                    avg_dist_p[each_key] = map(add,avg_dist_p[each_key],fft.fft([float(x) for x in each_p[each_key].split(',')]))
    
    for each_key in avg_dist_p.keys():
        avg_dist_p[each_key] = [x/float(p_counter) for x in avg_dist_p[each_key]]


    avg_dist_q = dict()
    q_counter = 0
    for each_q in q_feat:
        q_counter+=1
        if len(avg_dist_q)==0:
            for each_key in each_q.keys():
                if each_key != 'key':
                   avg_dist_q.update({each_key:fft.fft([float(x) for x in each_q[each_key].split(',')])})
        else:
            for each_key in each_q.keys():
                if each_key != 'key':
                   avg_dist_q[each_key] = map(add,avg_dist_q[each_key],fft.fft([float(x) for x in each_q[each_key].split(',')]))
    
    for each_key in avg_dist_q.keys():
        avg_dist_q[each_key] = [x/float(q_counter) for x in avg_dist_q[each_key]]


    # Ploting the distribution using histogram
    # Well...let's do it using matlab first...so output those data
    myplot(avg_dist_p['gyroX'])
    myplot(avg_dist_q['gyroX'])

if __name__=='__main__':
    main()
