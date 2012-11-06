# Wrapper and interface to libsvm tools.
# Using libsvm toolkit from http://www.csie.ntu.edu.tw/~cjlin/libsvm/
# Using x64 libsvm.dll from http://www.shenzousite.com/LibSVM.htm
# Last update: 31 Oct 2012

import sys, random, math
from Param import *     # Import class Param from file Param.py
from svmutil import *

# Methods

# Given a set of data, divide the data into k partitions and train a model from each partition.
# The model with the best accuracy is returned together with the avg_accuracy across the entire
# spectrum of data
# @params
#   labels -    A list containing the class labels. Each index corresponds to an instance in values.
#               Can also be a dictionary with no values provided or an svm_problem object.
#   values -    A 2d list containing the instances. Each row represents 1 instance. Each col represents
#               1 feature.
def xTrain(labels, values=None, k=10, rand=True):
    # Split data into k partitions
    partitions = split(labels, values, k, rand)
    best_model = None
    best_acc = -1
    avg_acc = 0
    count = 0
    

    if isinstance(labels, dict):
        values = [j for i in labels.itervalues() for j in i.itervalues()]
        labels = [i + 1 for i in range(len(labels.values())) for j in range(len(labels[labels.keys()[i]]))]

    if values != None:
        optParam = Param()
        print "Searching for optimal parameters..."
        optParam.c, optParam.g = getOptCG(labels, values)
        print "c: " + str(optParam.c) + " g: " + str(optParam.g)
        print " "

        # For each partition, train a model and check the accuracy of the partition's test data against
        # the model. The highest accuracy model will be the model returned. The accuracy returned is the
        # average accuracy of all the partitions
        for i in partitions.iter:
            print "Training iteration " + str(count + 1) + ".."
            # Train the model using the partition training data
            model = svmtrain(i.train.labels, i.train.values, optParam.c, optParam.g)
            # Get a list of predictions for the testing data
            pred = svmtest(i.test.values, model)
            # Find the accuracy of the test data predicted by the model
            acc, x1, x2 = evaluations(i.test.labels, pred)

            # Store the model with the best accuracy
            if acc > best_acc:
                best_acc = acc
                best_model = model

            print "Iteration " + str(count + 1) + " accuracy: " + str(acc)
            avg_acc += acc
            count += 1

        # Get the avg accuracy
        avg_acc /= count

        print " "
        print "xTrain completed."
        return model, avg_acc
        
def split(labels, values=None, k=5, rand=True):

    if isinstance(labels, dict):
        values = [j for i in labels.itervalues() for j in i.itervalues()]
        labels = [i + 1 for i in range(len(labels.values())) for j in range(len(labels[labels.keys()[i]]))]

    if values != None:
        # Normalize data
        values, meanVect, stdVect = normalise(values)

        print "Patitioning into " + str(k) + " parts."

        if rand:
            randStart = random.randint(0, len(labels))
        else:
            randStart = 0
        step = len(labels) / k  # Each patition size
        splitPts = range(randStart, len(labels) + randStart, step)
        partitions = []
        for i in range(len(splitPts)):
            stPt = splitPts[i] % len(labels)
            endPt = splitPts[(i+1) % len(splitPts)] - 1 # To handle circular problems
            midPt1 = (stPt + endPt) / 2
            midPt2 = midPt1 + 1

            if endPt < stPt:
                midPt1 = len(labels) - 1
                midPt2 = 0

            partitionLabels = labels[stPt:midPt1 + 1]
            partitionLabels.extend(labels[midPt2:endPt + 1])
            partitionValues = values[stPt:midPt1 + 1]
            partitionValues.extend(values[midPt2:endPt + 1])
            partition = DataSet(partitionLabels, partitionValues)
            partitions.append(partition)

        print str(len(partitions)) + " partitions created."
        distPartitions = Partitions(partitions)

        return distPartitions

def normalise(values, val=None, meanVect=None, stdVect=None):
    if values == "reverse":
        result = []
        result.extend(val)
        for i in range(len(result)):
            for j in range(len(result[i])):
                result[i][j] = result[i][j] * stdVect[j] + meanVect[j]

        return result
    else:
        if isinstance(values, list):
            meanVect = calMean(values)
            stdVect = calStd(values, meanVect)

        if values == "apply":
            result = []
            result.extend(val)
        else:
            result = []
            result.extend(values)

        for i in range(len(result)):
            for j in range(len(result[i])):
                result[i][j] = (float(result[i][j]) - meanVect[j])
                if stdVect[j] != 0:
                    result[i][j] / stdVect[j]

        if values == "apply":
            return result
        else:
            return result, meanVect, stdVect

def calMean(values):
    result = [0 for i in range(len(values[0]))]
    for i in range(len(values)):
        for j in range(len(values[i])):
            result[j] += values[i][j]

    #print "Result: " + str(result)
    for i in range(len(result)):
        result[i] = float(result[i]) / float(len(values))

    return result

def calStd(values, meanVect=None):
    if meanVect == None:
        meanVect = calMean(values)
        
    result = [0 for i in range(len(values[0]))]
    for i in range(len(values)):
        for j in range(len(values[i])):
            result[j] += (float(values[i][j]) - meanVect[j]) ** 2

    for i in range(len(result)):
        result[i] = float(result[i]) / float(len(values) - 1)
        result[i] = math.sqrt(result[i])

    return result

# Trains an svm model using C-svm and the RBF kernel using optimal parameters
# @params
#   labels - a list containing the class labels. Each index corresponds to an instance in values.
#            Can also be a dictionary  with nothing for values
#   values - a 2d list containing the instances. Each row represents 1 instance. Each col represents 1 feature
def svmtrain(labels, values=None, c=None, g=None):

    # If Dictionary
    if isinstance(labels, dict):        
        values = [j for i in labels.itervalues() for j in i.itervalues()]
        labels = [i + 1 for i in range(len(labels.values())) for j in range(len(labels[labels.keys()[i]]))]

    if values != None:
        
        optParam = Param()
        optParam.c = c
        optParam.g = g
        if c == None or g == None:
            # Retrieve optimal c and g
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

#def partitions(labels, values=None):
    # Check data type

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
