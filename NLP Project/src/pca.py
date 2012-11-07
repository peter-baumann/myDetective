#import matplotlib.pyplot as plt
import pylab as pl
import numpy as np
from sklearn.decomposition import PCA
import Main

def get_essay_vectors():
    Main.settings = {'FunctionWordFrequency' : False,
        'BigramFrequency' : False,
        'TrigramFrequency' : False,
        'AverageWordLength' : True,
        'AverageSentenceLength' : True,
        'LexicalDiversity' : True}

    authors = Main.getAuthors()
    essay_vectors = {}
    for author, data in authors.iteritems():
        essay_vectors[author] = {}
        for file in data:
            essay_vectors[author][file[0]]=Main.getAttributeVector(file[1])
    return essay_vectors
    
#print get_essay_vectors()    

variables = []
authors = []
author_names = []
essay_names = []

i=-1
for author, data in get_essay_vectors().iteritems():
    i += 1
    author_names.append(author)
    for essay, data in data.iteritems():
        authors.append(i)
        variables.append(data)
        essay_names.append(essay)

print "LEN VARIABLES "+ str(len(variables))

print authors
colors = ("#FF0000", "#00FF00", "#0000FF", "#FFFF00")
markers = ("o", "D", "s", "x")
#print variables
#print authors
#print author_names
#print essay_names

X = np.array(variables)
y = np.array(authors)

target_names = np.array(author_names)

pca = PCA(n_components=2)
X_r = pca.fit(X).transform(X)

# Percentage of variance explained for each components
#print pca.explained_variance_

print len(colors)
print len(variables)
print len(target_names)


print markers
print markers[2]

pl.figure()
print colors
for i, target_name in zip(range(len(variables)), target_names):
    pl.scatter(X_r[y==i,0], X_r[y==i,1], c=colors[i%4], marker=markers[(i/4)%4], label=target_name)
pl.legend()
pl.title('PCA of the BAWE essay dataset')

pl.show()

"""
markers
'o' circle
'D' diamond
'6' caretup
's' square
"""

