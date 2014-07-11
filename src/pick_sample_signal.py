import sys
import os
import math
import json
import ast
import matplotlib.pyplot as plt
import numpy as np
import random
import matplotlib

def select_random_sample(letter,all_signal_list,dim_name):
    rand_index = int(random.random()*10)+1
    i = 0
    for each_signal in all_signal_list:
        if letter == each_signal['key']:
            i+=1
            if i==rand_index:
                raw_signal = [float(x) for x in each_signal[dim_name].split(",")]
                break

    return raw_signal

def select_sample_signal(all_signal_list,input_phrase,dim_name):
    # repalce space with b
    input_phrase = input_phrase.replace(" ","b")
    raw_signal_list = []
    for each_letter in input_phrase:
        raw_signal_list.append(select_random_sample(each_letter,all_signal_list,dim_name))

    return raw_signal_list

def read_file_to_dict(json_file):
    json_data = open(json_file).read()
    data = ast.literal_eval(json_data)
    return data

def annotate_group(name, xspan, ax=None):
    """Annotates a span of the x-axis"""
    def annotate(ax, name, left, right, y, pad):
        arrow = ax.annotate(name,
                xy=(left, y), xycoords='data',
                xytext=(right, y-pad), textcoords='data',
                annotation_clip=False, verticalalignment='top',
                horizontalalignment='center', linespacing=2.0,
                arrowprops=dict(arrowstyle='-', shrinkA=0, shrinkB=0,
                                connectionstyle='angle,angleB=90,angleA=0,rad=5')
                )
        return arrow
    if ax is None:
        ax = plt.gca()
    ymin = ax.get_ylim()[0]
    ypad = 0.01*np.ptp(ax.get_ylim())
    xcenter = np.mean(xspan)
    left_arrow = annotate(ax, name, xspan[0], xcenter, ymin, ypad)
    right_arrow = annotate(ax, name, xspan[1], xcenter, ymin, ypad)
    return left_arrow, right_arrow

def plot_signal(signal_list,input_phrase):
    all_signal = []
    each_len = 0
    for each in signal_list:
        all_signal = all_signal + each
        each_len = len(each)
    
    y = np.array(all_signal)
    plt.plot(y)
    i = 0
    groups = list()
    for each_letter in input_phrase:
        group_tuple = each_letter,(i*each_len,(i+1)*each_len-1)
        groups.append(group_tuple)
        i += 1

    for name, xspan in groups:
        annotate_group(name, xspan)
    ax = plt.gca()
    plt.setp(ax.get_xmajorticklabels(), visible=False)
    plt.show()

def main():
    files = ['first-two-lines.json','F-to-end.json']
    input_phrase = "hpp aee ypu dppbg"

    all_signal = []

    for each_file in files:
        current_signal = read_file_to_dict(each_file)
        all_signal = all_signal+current_signal

    signal_list = select_sample_signal(all_signal,input_phrase,"gyroX")
    plot_signal(signal_list,input_phrase)

if __name__=="__main__":
    main()
