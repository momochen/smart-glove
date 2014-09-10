import os
import sys
from joblib import Parallel, delayed

class test:
    
    def __init__(self):
        self.input_list = [1,2,3,4,5]
        self.b = {1:1,2:2,3:3,4:4,5:5}
    def p(self):
        print Parallel(n_jobs=10)(delayed(pp)(x,self.b) for x in self.input_list)

def p_p(a,b):
    return a*b
if __name__=="__main__":
    t = test()
    t.p()
