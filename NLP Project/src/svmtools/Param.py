class Param(object):
    def __init__(self):
        self._c = 0
        self._g = 0
        self._cset = []
        self._gset = []
        self._nfold = 5     # Default 5 fold cross-validation

    @property
    def nfold(self):
        return self._nfold

    @nfold.setter
    def nfold(self, value):
        self._nfold = value
        
    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, value):
        self._c = value

    @property
    def g(self):
        return self._g

    @g.setter
    def g(self, value):
        self._g = value

    @property
    def libsvm(self):
        return "-c " + str(self._c) + " -g " + str(self._g) + " -q"

    @property
    def cset(self):
        return self._cset

    @cset.setter
    def cset(self, value):
        if isinstance(value, list):
            self._cset = value

    @property
    def gset(self):
        return self._gset

    @gset.setter
    def gset(self, value):
        if isinstance(value, list):
            self._gset = value

class Partitions():
    def __init__(self, partitions):
        self.iter = []
        for i in range(len(partitions)):
            testSet = partitions[i]
            trainSetValues = []
            trainSetLabels = []
            for j in range(len(partitions)):
                if j != i:
                    trainSetValues.extend(partitions[j].values)
                    trainSetLabels.extend(partitions[j].labels)
            
            trainSet = DataSet(trainSetLabels, trainSetValues)
            partition = Partition(trainSet, testSet)
            self.iter.append(partition)

class Partition():
    def __init__(self, trainSet, testSet):
        self.train = trainSet
        self.test = testSet

class DataSet():
    def __init__(self, labels, values):
        self.labels = labels
        self.values = values