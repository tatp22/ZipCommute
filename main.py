import ml
import csv
import plotting
import numpy as np
import numpy.linalg as la
import copy

locs = {} # {zip : [(lat, long), commute time]}
accd = []
temp = {}
k = 300
iters = 3

def parseCSV(filename, fileno):
	with open(filename) as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		rnum = 0
		for row in reader:
			if rnum == 0:
				rnum += 1 #don't read header...
			else:
				if fileno == 0:
					if row[5] == "PRIMARY" and row[6] != "" and float(row[6]) > 20 and float(row[7]) < -50 and float(row[7]) > -128:
						locs[int(row[1])] = [(float(row[6]),float(row[7]))]
				else:
					if int(row[1]) in locs and row[3] != "":
						locs[int(row[1])].append(float(row[3]))

def readInFiles():
	parseCSV("free-zipcode-database.csv",0)
	parseCSV("commute_times_us_zipcode_2011.csv",1)

def placeInLists(x,y,zips):
	for key in locs:
		y.append(locs[key][0][0])
		x.append(locs[key][0][1])
		zips.append(key)
	x = np.array(x)
	y = np.array(y)

#This filter is supposed to get rid of the outlying zip codes quickly, ones that don't rely on cities
def getRidOfRuralPointsFast(x,y,zips):
	locations = np.zeros((len(x),2))
	locations[:,0] = x
	locations[:,1] = y
	iters = 0
	tol = .05
	for i in range(len(locations)):
		iters += 1
		if iters % 500 == 0:
			print(iters)
		if locations[i][0] in temp and temp[locations[i][0]] == locations[i][1]:
			continue
		else:
			temp[locations[i][0]] = locations[i][1]
		max_dist = 50
		for j in range(i+1,min(len(locations),100+i)):
			d = la.norm(locations[i] - locations[j])
			if d < max_dist:
				max_dist = d
			if max_dist < tol:
				break
		for j in range(i-100,i):
			d = la.norm(locations[i] - locations[j])
			if d < max_dist:
				max_dist = d
			if max_dist < tol:
				break
		if max_dist > tol:
			del locs[zips[i]]

def filterLocs():
	temp_locs = copy.copy(locs)
	for key in temp_locs:
		if len(locs[key]) == 1:
			del locs[key]

def getLocDict():
	d = {}
	for key in locs:
		if locs[key][0] not in d:
			d[locs[key][0]] = 1
		else:
			d[locs[key][0]] += 1
	return d


def getClosePoints(key):
	points = 0
	thresh = .05
	arr1 = np.array([locs[key][0][0], locs[key][0][1]])
	for key1 in locs:
		arr2 = np.array([locs[key1][0][0], locs[key1][0][1]])
		n = la.norm(arr1-arr2)
		if n < thresh:
			points += 1
	return points

def citify(x,y,zips):
	d = getLocDict()
	n = 2
	m = 3 #1 + whatYouWant, it counts itself
	iters = 0
	for i in range(len(x)):
		iters += 1
		if iters % 500 == 0:
			print(iters)
		tup = (y[i],x[i])
		if d[tup] >= n:
			continue #n zips in the same place, move on...
		else:
			#here comes the slow step, although it shouldn't be that bad
			closePoints = getClosePoints(zips[i])
			if closePoints < m:
				del locs[zips[i]]

def getDist(p1,p2):
	return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**.5

def superRemove(x,y,zips):
	d = getLocDict()
	maxLen = 300
	c = .18
	mainList = []
	pointsToInclude = []
	for key in sorted(d, key=d.get, reverse=True):
		for i in range(len(mainList)):
			dist = getDist(mainList[i], key)
			if dist < d[key]*c:
				pointsToInclude.append(key)
				break
		if len(pointsToInclude) == 0 or pointsToInclude[-1] != key:
			if len(mainList) < maxLen:
				mainList.append(key)
	for key, v in list(locs.items()):
		if locs[key][0] not in mainList and locs[key][0] not in pointsToInclude:
			del locs[key]

def interactWithUser():
	print("Commute times calculated.")
	str = ""
	while str != "n":
		print("Type in your zip to see where it ranks in commute times, or (n) to quit:")
		str = input()
		if str == "n":
			break
		try:
			str = int(str)
			if str not in locs:
				print("Sorry, your zip code was not found. This could be beacuse:")
				print("a. The algorithm counted your zip code as a rural location")
				print("b. The zip code you entered is not a valid zip code")
			else:
				print("Your zip code was found! The aveage commute time for your zip is: ", locs[str][1])
				print("Your metro area ranks at ", 4,"out of a calculated ",k," metro areas in the country.")
		except:
			print("Please enter a valid zip code")
			

def main():
	x = []
	y = []
	zips = []
	readInFiles()
	placeInLists(x,y,zips)
	print("Num points initially: ", len(x))
	plotting.scatterBasic(x,y)
	superRemove(x,y,zips)
	x = []
	y = []
	zips = []
	placeInLists(x,y,zips)
	print("Num points after super filter: ", len(x))
	plotting.scatterBasic(x,y)
	filterLocs()
	x = []
	y = []
	zips = []
	placeInLists(x,y,zips)
	print("Num points after removing places with no commute times: ", len(x))
	plotting.scatterBasic(x,y)
	'''
	citify(x,y,zips)
	x = []
	y = []
	zips = []
	placeInLists(x,y,zips)
	print("Num points after second filter: ", len(x))
	'''
	#plotting.scatterBasic(x,y)
	#1. Cluster nodes into n (250 for now) groups based on k-means
	centers, preds, locs = ml.kmeans(k, iters, x,y)
	plotting.plotCenter(centers)
	plotting.plotScatterColor(locs,preds,k)
	#2. With these clusters, get the average commute time with all the zip codes
	#3. Rank them somehow... Maybe I can use the names from earlier? Or maybe some machine learning can come into play...
	interactWithUser()

main()