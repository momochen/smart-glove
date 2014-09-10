import os
import sys
from sklearn import svm
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import operator
from operator import itemgetter, attrgetter
from move2stc import Move2Stc
import math

class Ensemble_Learning:

    def __init__(self,feature_mat,target_mat,test_feat_mat,test_target_mat):
        self.feature_mat = feature_mat 
        self.target_mat = target_mat
        self.test_feat_mat = test_feat_mat
        self.test_target_mat = test_target_mat
        self.trained_model_list = []
        self.cm_dict = dict()

    # testing data with correct words and predicted words aligned
    def verbose_test(self):
        # Print the original code
        print "True:"
        print ','.join([x for x in self.test_target_mat])
        print "Predicted:"
        prediction_result = []
        for each_model in self.trained_model_list:
            print ','.join([x for x in each_model.predict(self.test_feat_mat)])

    # confusion matrix for each labeled-class; 
    def generate_confusion_matrix(self):
        print "gernerating confusion matrix..."
        X = self.feature_mat
        y = self.target_mat
        cm_dict = dict()
        all_label = list(set(y))
        for i in range(len(all_label)):
            cm_dict.update({all_label[i]:dict((label,0) for label in all_label)})

        # Average over times
        k = 0

        while k < 5:
            X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

            rf = RandomForestClassifier(n_estimators=200)
            y_pred = rf.fit(X_train,y_train).predict(X_test)
            cm = confusion_matrix(y_test,y_pred)

            for i in range(len(y_test)):
                cm_dict[y_test[i]][y_pred[i]]+=1
            k+=1

        # Normalize the dict
        for each_label in cm_dict.keys():
            total_test = sum(cm_dict[each_label].values())
            for each_sub_label in cm_dict[each_label].keys():
                cm_dict[each_label][each_sub_label] = float(cm_dict[each_label][each_sub_label])/float(total_test)

        #print "Confusion matrix:"
        #print cm
        #print  "Confusion dictionary"
        #print cm_dict
        '''
        plt.matshow(cm)
        plt.title("confusion matrix")
        plt.colorbar()
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.show()
        '''
        self.cm_dict = cm_dict
        return cm_dict

    def test_single(self,ft_row):
        votes = dict()
        for each in self.trained_model_list:
            label = str(each.predict(ft_row)[0])
            if not votes.has_key(label):
                votes.update({label:1})
            else:
                votes[label]+=1
        return max(votes.iteritems(), key=operator.itemgetter(1))[0]
        
    def generate_scores(self):
        print "generanting scores..."
        score_list = []
        for model in self.ml_model_list:
            # As for each model, return the mean and deviation of the score
            mean,dev = model(self,self.feature_mat,self.target_mat)
            score_list.append([mean,dev])
        print score_list

    def svm(self,feature_mat,target_mat):
        # svm in python can only deal with integer index
        m2s = Move2Stc()
        target_mat = np.array([int(m2s.label2code(x),2) for x in target_mat])
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
        rf = RandomForestClassifier(n_estimators=150,max_features=int(math.sqrt(len(feature_mat[0]))))
        trained_rf = rf.fit(feature_mat,target_mat)
        self.trained_model_list.append(trained_rf)
        scores = cross_validation.cross_val_score(rf,feature_mat,target_mat,cv=5)
        return (scores.mean(),scores.std())
    
    def get_ml_model(self):
        return self.trained_model_list

    ml_model_list = [random_forest]
