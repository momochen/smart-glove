import os
import sys
from sklearn import svm
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class Ensemble_Learning:

    def __init__(self,feature_mat,target_mat,test_feat_mat,test_target_mat):
        self.feature_mat = feature_mat 
        self.target_mat = target_mat
        self.test_feat_mat = test_feat_mat
        self.test_target_mat = test_target_mat
        self.trained_model_list = []
    
    # testing data with correct words and predicted words aligned
    def verbose_test(self):
        # Print the original code
        print "Ground Truth:"
        print ','.join([x for x in self.test_target_mat])
        print "Predictions:"
        prediction_result = []
        for each_model in self.trained_model_list:
            print ','.join([x for x in each_model.predict(self.test_feat_mat)])

    def generate_scores(self):
        print "gen scores"
        score_list = []
        for model in self.ml_model_list:
            # As for each model, return the mean and deviation of the score
            mean,dev = model(self,self.feature_mat,self.target_mat)
            score_list.append([mean,dev])
        print score_list


    def svm(self,feature_mat,target_mat):
        # svm in python can only deal with integer index
        target_mat = np.array([ord(x) for x in target_mat])
        # Available kernels are: linear,polynomial,rbf,sigmoid
        clf = svm.SVC(kernel='rbf')
        trained_svm = clf.fit(feature_mat,target_mat)
        self.trained_model_list.append(trained_svm)
        scores = cross_validation.cross_val_score(clf,feature_mat,target_mat,cv=5)
        return (scores.mean(),scores.std())


    def random_forest(self,feature_mat,target_mat):
        #print "sample target:",target_mat[0]
        #target_mat = np.array([ord(x) for x in target_mat])

        target_mat = np.array([x for x in target_mat])

        rf = RandomForestClassifier(n_estimators=100)
        trained_rf = rf.fit(feature_mat,target_mat)
        self.trained_model_list.append(trained_rf)
        scores = cross_validation.cross_val_score(rf,feature_mat,target_mat,cv=5)
        return (scores.mean(),scores.std())

    ml_model_list = [random_forest]
