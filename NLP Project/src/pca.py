import pylab as pl
import numpy as np
from sklearn.decomposition import PCA
import Main


class PCAPlot():
    def __init__(self, unknown=None):
        self.variables = []
        self.authors = []
        self.author_names = []
        self.essay_names = []
        i=-1

        self.essay_vectors = Main.get_essay_vectors(unknown)

        for author, data in self.essay_vectors.iteritems():
            i += 1
            self.author_names.append(author)
            for essay, data in data.iteritems():
                self.authors.append(i)
                self.variables.append(data)
                self.essay_names.append(essay)

        # Add padding zeros to make vectors uniform length
        max_length = max(map(len, self.variables))
        for i in range(len(self.variables)):
            self.variables[i].extend([0] * (max_length - len(self.variables[i])))

        X = np.array(self.variables)
        self.y = np.array(self.authors)
        self.target_names = np.array(self.author_names)

        self.pca = PCA(n_components=2)
        self.X_r = self.pca.fit(X).transform(X)

    def plot(self, highlight=[]):
        colors = ("#FF0000", "#00FF00", "#0000FF", "#FFFF00")
        markers = ("o", "D", "s", "x")

        pl.figure()

        for i, target_name in zip(range(len(self.variables)), self.target_names):
            if highlight: 
                size = 5
                if target_name in highlight : size=100 
            else: size = 50
            if target_name == "unknown": size=250 
            pl.scatter(self.X_r[self.y==i,0], self.X_r[self.y==i,1], 
                    s=size, c=colors[i%4], marker=markers[(i/4)%4],
                    label=target_name)
        pl.legend()
        pl.title('PCA of the BAWE essay dataset')

        pl.show()
