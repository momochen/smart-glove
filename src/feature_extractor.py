import os
import sys
import types
import numpy
from scipy.fftpack import rfft
from numpy import linalg as LA
import operator

class Feature_Target_Extractor:

    def __init__(self,feature_data_dict):
        # Extract the time sereis data from different dimensions
        # Convert the literals to float
        for each_key in feature_data_dict:
            if each_key != 'key':
                if type(feature_data_dict[each_key])==type(str()):
                    feature_data_dict[each_key] = [float(x.lower()) for x in feature_data_dict[each_key].split(',')]
                elif type(feature_data_dict[each_key])==type(list()):
                    feature_data_dict[each_key] = [float(x) for x in feature_data_dict[each_key]]
        self.feature_data_dict = feature_data_dict
        self.feat_list = []
        self.target = ''


    def get_feat_target_list(self):
        for each_key in self.feature_data_dict.keys():
            if each_key != 'key':
                for func in self.feature_func_list:
                    if func.__name__=='feat_f_fft':
                        self.feat_list = self.feat_list+func(self,self.feature_data_dict[each_key]).tolist()
                    else:
                        self.feat_list.append(func(self,self.feature_data_dict[each_key]))
            elif each_key == 'key':
                self.target = self.feature_data_dict[each_key]

        return (self.feat_list,self.target)

    def feat_f_fft(self,ts):
        return rfft(ts)

    def feat_t_mean(self,ts):
        return numpy.mean(ts)

    def feat_t_high(self,ts):
        return max(ts)

    def feat_t_low(self,ts):
        return min(ts)

    def feat_t_skew(self,ts):
        return abs(max(ts))-abs(min(ts))

    def feat_t_frobenius_norm(self,ts):
        return LA.norm(ts)

    def feat_t_one_norm(self,ts):
        return LA.norm(ts,1)

    def feat_t_1st_drv_high(self,ts):
        return max(numpy.gradient(ts))

    def feat_t_2nd_drv_high(self,ts):
        return max(numpy.gradient(numpy.gradient(ts)))

    def feat_t_1st_drv_low(self,ts):
        return min(numpy.gradient(ts))

    def feat_t_2nd_drv_low(self,ts):
        return min(numpy.gradient(numpy.gradient(ts)))

    feature_func_list = [feat_f_fft,feat_t_mean,feat_t_high,
        feat_t_low,feat_t_skew,feat_t_frobenius_norm,
        feat_t_one_norm,feat_t_1st_drv_high,feat_t_2nd_drv_high,
        feat_t_1st_drv_low,feat_t_2nd_drv_low]
