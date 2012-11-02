'''
Created on 02.11.2012

@author: Peter
'''

from svmtools.svmutil import *
from svmtools.SvmInterface import *

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def stub(self):
        y, x = svm_read_problem('svmtools/train.lsvm')
        model = svmtrain(y, x)
        pred = svmtest(x, model)
        evaluations(y, pred)