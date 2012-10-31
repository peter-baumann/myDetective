# Wrapper and interface to libsvm tools.
# Using libsvm toolkit from http://www.csie.ntu.edu.tw/~cjlin/libsvm/
# Using x64 libsvm.dll from http://www.shenzousite.com/LibSVM.htm
# Last update: 31 Oct 2012

import sys
from Param import Param     # Import class Param from file Param.py
from svmutil import *

# Methods

# Trains an svm model using C-svm and the RBF kernel using optimal parameters
# @params
#   labels - a list containing the class labels. Each index corresponds to an instance in values.
#            Can also be a dictionary  with nothing for values
#   values - a 2d list containing the instances. Each row represents 1 instance. Each col represents 1 feature
def svmtrain(labels, values=None):
    # If Dictionary
    if isinstance(labels, dict):        
        values = [j for i in labels.itervalues() for j in i.itervalues()]
        labels = [i + 1 for i in range(len(labels.values())) for j in range(len(labels[labels.keys()[i]]))]

    if values != None:
        # Retrieve optimal c and g
        optParam = Param()
        optParam.c, optParam.g = getOptCG(labels, values)    
    
        # Train model with optimal c and g
        prob = svm_problem(labels, values)
        m = svm_train(prob, optParam.libsvm)
    
        # Return model
        return m
    else:
        raise TypeError("Values not provided for the arguments")

# Using a provided model, generates the predicted labels for each instance provided
# @params
#   values - a 2d list containing the instances. Same as values in svmtrain.
#            Can also be a dictionary. In that case, only the values are extracted.
#   model - a model trained using svmtrain()
def svmtest(values, model):    
    if isinstance(values, list) or isinstance(values, dict):
        # If dictionary
        if isinstance(values, dict):        
            values = [j for i in values.itervalues() for j in i.itervalues()]
        
        # Fix if single example (first element is a float, long, int)
        if isinstance(values[0], (float, long, int)):
            values = [values]
    
        # Test model with provided data
        labels = [0 for i in range(len(values))]
        pred, acc, p_vals = svm_predict(labels, values, model)
    
        # Return prediction
        return pred
    else:
        raise TypeError("Inappropriate argument provided for values")

# Searches a grid for the optimal c and g values for a given dataset
def getOptCG(labels, values):
    # Format data for subsequent methods

    # Set up cross-validation settings
    param = Param()    
    param.cset = range(-5, 15, 2)
    param.gset = range(3, -15, -2)
    param.nfold = 10
    prob = svm_problem(labels, values)
    rVal = [[0 for col in range(len(param.cset))] for row in range(len(param.gset))];

    # Cross-validation to get optimal parameters
    for i in range(len(param.gset)):
        param.g = 2 ** param.gset[i]

        for j in range(len(param.cset)):
            param.c = 2 ** param.cset[j]
            testParam = svm_parameter(param.libsvm)
                
            # Train on learning data with x-validation and store result
            rVal[i][j] = svm_train(prob, param.libsvm + " -v " + str(param.nfold))


    # Select the parameters with highest accuracy
    min_val, loc = getMax(rVal)
    g = 2 ** param.gset[loc[0]]
    c = 2 ** param.cset[loc[1]]

    return c, g

def getMax(_list):
    max_val = -1
    coord = []    
    
    for i in range(len(_list)):
        # Recursively call itself to get max value.
        # This handles any dimension of _list
        if isinstance(_list[i], list):
            val, loc = getMax(_list[i])
        else:
            val = _list[i]
            
        if val > max_val:
            max_val = val
            coord =[i]
            if vars().has_key('loc'):
                coord.extend(loc)

    return max_val, coord
# Methods end

if __name__ == '__main__':
    # If called on its own
    # Remove if not needed in future
    sys.exit(0)
