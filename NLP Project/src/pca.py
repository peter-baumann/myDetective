import pylab as pl
import numpy as np
from sklearn.decomposition import PCA
import Main


def get_essay_vectors():
    Main.settings = {'FunctionWordFrequency' : True,
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
            # convert all items to float, because PCA library does not
            # like the decimal.Decimal type
            vector = [float(i) for i in Main.getAttributeVector(file[1])]
            essay_vectors[author][file[0]]=vector
    return essay_vectors


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


colors = ("#FF0000", "#00FF00", "#0000FF", "#FFFF00")
markers = ("o", "D", "s", "x")

X = np.array(variables)
y = np.array(authors)
target_names = np.array(author_names)

pca = PCA(n_components=2)
X_r = pca.fit(X).transform(X)

pl.figure()
print colors
for i, target_name in zip(range(len(variables)), target_names):
    pl.scatter(X_r[y==i,0], X_r[y==i,1], c=colors[i%4], marker=markers[(i/4)%4], label=target_name)
pl.legend()
pl.title('PCA of the BAWE essay dataset')

pl.show()
