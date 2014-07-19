import os
import sys
from os import listdir
from os.path import isfile, join
import json
from feature_extractor import Feature_Target_Extractor
from ensemble_learning import Ensemble_Learning
import numpy

def main():
    data_dir_path = "../data/training-data/"
    expr_data_files = [ f for f in listdir(data_dir_path) if f.endswith(".json") ]
    train_data_all = []
    test_data_all = []
    cur_dir_list = os.getcwd().split("/")

    for each_file in expr_data_files:
        train_file = json.loads(open("/".join(cur_dir_list[:(len(cur_dir_list)-1)])+"/data/training-data/"+each_file).read())
        train_data_all = train_data_all + train_file

    for each_file in expr_data_files:
        test_file = json.loads(open("/".join(cur_dir_list[:(len(cur_dir_list)-1)])+"/data/training-data/"+each_file).read())
        test_data_all = test_data_all + test_file

    # Pick some samples from all the data as the testing data

    train_data_mat = []
    train_target_mat = []

    for each_sample in train_data_all:
        """
        if len(each_sample["accY"])==0:
            print "error training data",each_sample["key"]
            exit()
        """
        fte = Feature_Target_Extractor(each_sample)
        feat,target = fte.get_feat_target_list()
        train_data_mat.append(feat)
        train_target_mat.append(target)

    test_data_mat = []
    test_target_mat = []

    for each_sample in test_data_all:
        fte = Feature_Target_Extractor(each_sample)
        feat,target = fte.get_feat_target_list()
        test_data_mat.append(feat)
        test_target_mat.append(target)
    
    train_data_mat = numpy.array(train_data_mat)
    train_target_mat = numpy.array(train_target_mat)
    el = Ensemble_Learning(train_data_mat,train_target_mat,test_data_mat,test_target_mat)
    el.generate_scores()
    #el.verbose_test()

if __name__=='__main__':
    main()
