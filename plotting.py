import matplotlib.pyplot as plt
import numpy as np

def scatterBasic(x,y):
	plt.plot(x,y,"bo")
	plt.show()
	
def plotCenter(center):
	plt.plot(center[:,0], center[:,1], "r+",markersize=10)

def plotScatterColor(locs,preds,k):
	#we need 4 colors for this... (Thanks to that one UIUC proof)
	m = 10
	for i in range(k):
		plt.plot(locs[preds == i,0], locs[preds == i,1], 'o',c=np.random.rand(3,1))
	plt.show()