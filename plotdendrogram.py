from sklearn.cluster import spectral_clustering

import scipy,yaml
import pylab
import scipy.cluster.hierarchy as sch

# Generate random features and distance matrix.
x = scipy.rand(40)
D = scipy.zeros([40,40])
for i in range(40):
    for j in range(40):
        D[i,j] = abs(x[i] - x[j])

cfm=yaml.load(open(r'E:\elan projects\L2\resubmission\passed\meanmatrix.yaml','r'))
D=scipy.array( cfm._confusion)




Y = sch.linkage(D, method='centroid')
sch.dendrogram(Y,labels=cfm._values)


#pylab.show()
pylab.savefig('dendrogram.png')

labelsdis = spectral_clustering(D, n_clusters=5,
                                 assign_labels='discretize',
                                 random_state=None)
labelskm = spectral_clustering(D, n_clusters=5,
                                 assign_labels='kmeans',
                                 random_state=None)

labelsdis= sorted( zip(labelsdis.tolist(),cfm._values))
labelskm= sorted( zip(labelskm.tolist(),cfm._values))

print labelsdis
print labelskm
