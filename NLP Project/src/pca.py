import pylab as pl
import numpy as np
from sklearn.decomposition import PCA
import Main





variables = []
authors = []
author_names = []
essay_names = []
i=-1

print Main.get_essay_vectors()

for author, data in Main.get_essay_vectors().iteritems():
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
for i, target_name in zip(range(len(variables)), target_names):
    size=50
    if target_name == "unknown" : size=250 
    pl.scatter(X_r[y==i,0], X_r[y==i,1], s=size, c=colors[i%4], 
            marker=markers[(i/4)%4], label=target_name)
pl.legend()
pl.title('PCA of the BAWE essay dataset')

pl.show()
