import random
import numpy as np
import numpy.linalg as la

def fill_random(arr,locs):
	for i in range(len(arr)):
		randno = random.randint(0,len(locs))
		while locs[randno] in arr:
			randno = random.randint(0,len(locs))
		arr[i] = locs[randno]
	return arr

'''
@param k number of means
@param iters number of iterations of k-means algo
@param x,y coords of the center of each zip
@return centers (2,k)-length np array of the centers of the centroids
@return groups len(x) array of the groups that the coordinates will be placed into
'''
def kmeans(k, iters, x,y):
	n = len(x)
	groups = np.zeros(len(x), dtype=np.int)
	locs = np.zeros((len(x), 2))
	locs[:,0] = x
	locs[:,1] = y
	centers = np.zeros((k,2)) #each thing will be (x,y) of centroids
	centers = fill_random(centers,locs)
	for iter in range(iters):
		print(iter)
		for i,x in enumerate(locs):
			dist = [la.norm(x - centers[j],2) for j in range(k)]
			groups[i] = np.argmin(dist)
		centers = np.array([np.mean(locs[groups == i],axis=0) for i in range(k)])
	return centers, groups, locs