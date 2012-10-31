from matplotlib.mlab import PCA
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

raw_data = {
        "Author 1":
            { "Essay 1": [22, 23.5,0],
            "Essay 2": [22, 21.5,0],
            "Essay 3": [22, 22.4,0] },
        
        "Author 2":
            { "Essay 1": [2.3, 3.5,9],
            "Essay 2": [2.6, 1.5,9],
            "Essay 3": [2.9, 2.4,9] } }

raw_data = {
        "Author 1":
            { "Essay 1": [4.3, 23.5, 6.1, 4.3, 12.0, 0.9],
            "Essay 2": [3.6, 21.5, 6.6, 3.3, 11.2, 1.2],
            "Essay 3": [3.9, 22.4, 6.8, 4.1, 12.3, 3.9] },
        
        "Author 2":
            { "Essay 1": [2.3, 23.5, 8.1, 2.3, 11.0, 0.9],
            "Essay 2": [2.6, 21.5, 8.6, 1.3, 11.2, 1.2],
            "Essay 3": [2.9, 22.4, 8.8, 2.1, 11.3, 3.9] },

        "Unknown":
            { "Essay 1": [1.3, 22.5, 8.1, 2.1, 11.0, 0.8] } }


list_of_lists = []
list_of_authors = []

for author, data in raw_data.iteritems():
#    print author
    for essay, data in data.iteritems():
        list_of_authors.append(author)
        list_of_lists.append(data)

# Convert a list-of-lists into a numpy array
data_matrix = numpy.array(list_of_lists)

results = PCA(data_matrix)

# These are just for test, straight from tutorial at
# http://blog.nextgenetics.net/?e=42
# this will return an array of variance percentages for each component
print "results.fracs"
print results.fracs

# this will return a 2d array of the data projected into PCA space
print "results.Y"
print results.Y 

x = []
y = []
z = []
for item in results.Y:
#    print "** " + str(item)
    x.append(item[0])
    y.append(item[1])
    z.append(item[2])


plt.close('all') # close all latent plotting windows
fig1 = plt.figure() # Make a plotting figure
ax = Axes3D(fig1) # use the plotting figure to create a Axis3D object.
pltData = [x,y,z] 
#ax.scatter(pltData[0], pltData[1], pltData[2], 'bo') # make a scatter plot of blue dots from the data

for i in range(len(z)):
    ax.plot([x[i]],[y[i]],[z[i]], marker='o', markersize=10, label=list_of_authors[i])
    ax.text(x[i],y[i],z[i],list_of_authors[i], fontsize=16)
#   grid()

    print str(i) + list_of_authors[i]
 
# make simple, bare axis lines through space:
#xAxisLine = ((min(pltData[0]), max(pltData[0])), (0, 0), (0,0)) # 2 points make the x-axis line at the data extrema along x-axis 
#ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r') # make a red line for the x-axis.
#yAxisLine = ((0, 0), (min(pltData[1]), max(pltData[1])), (0,0)) # 2 points make the y-axis line at the data extrema along y-axis
#ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r') # make a red line for the y-axis.
#zAxisLine = ((0, 0), (0,0), (min(pltData[2]), max(pltData[2]))) # 2 points make the z-axis line at the data extrema along z-axis
#ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r') # make a red line for the z-axis.

#ax.plot(x,y,z, "r")
 
# label the axes 
ax.set_xlabel("x-axis label") 
ax.set_ylabel("y-axis label")
ax.set_zlabel("y-axis label")
ax.set_title("The title of the plot")
plt.show() # show the plot


