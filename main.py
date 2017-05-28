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
iters = 8

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

def getDist(p1,p2):
	return ((p1[0]-p2[1])**2 + (p1[1]-p2[0])**2)**.5

def removeFromDict(d,x,y):
	td = copy.copy(d)
	for i in range(len(x)):
		tup = (y[i],x[i])
		for key in td:
			if key == tup:
				del d[key]
				break
	return d
	
def removeFromLocs(l):
	td = copy.copy(locs)
	for key in td:
		if locs[key][0] not in l:
			del locs[key]
	
def tupelize(x,y):
	l = []
	for i in range(len(x)):
		l.append((y[i],x[i]))
	return l

#initializer
def superRemove(x,y,zips):
	d = getLocDict()
	maxLen = 100
	c = .6
	accx = []
	accy = []
	for key in sorted(d, key=d.get, reverse=True):
		if len(accx) == maxLen:
			break
		addToList = True
		for i in range(len(accx)):
			tup = (accx[i],accy[i])
			if getDist(tup, key) < c*d[key]:
				addToList = False
		if addToList:
			accx.append(key[1])
			accy.append(key[0])
	d = removeFromDict(d,accx,accy)
	rootx = copy.copy(accx)
	rooty = copy.copy(accy)
	iters = 0
	c = .25
	for key in d:
		iters += 1
		if iters % 1000 == 0:
			print(iters)
		for i in range(len(rootx)):
			tup = rootx[i],rooty[i]
			if getDist(tup,key) < c*d[key]:
				accx.append(key[1])
				accy.append(key[0])
				break
	l = tupelize(accx,accy)
	roots = tupelize(rootx, rooty)
	removeFromLocs(l)
	x = []
	y = []
	zips = []
	placeInLists(x,y,zips)
	return x,y,roots,maxLen

def interactWithUser(d):
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
				print("The commute time for your geographical location is: ",d[str][1])
				print("Your metro area ranks at ", d[str][2],"out of a calculated ",k," metro areas in the country.")
		except:
			print("Please enter a valid zip code")

#get info about each individual zip code...
def getZipInfoDict(preds,alocs,zips):
	ret = {} # {zip : [group, group commute time, rank]}
	groups = {} # {group : [zipcodes, groupCommuteTime, rank]}
	for i in range(len(alocs)):
		if preds[i] not in groups:
			groups[preds[i]] = [[zips[i]],0,0]
		else:
			groups[preds[i]][0].append(zips[i])
	for key in groups:
		avg = 0
		arr = groups[key][0]
		for i in range(len(arr)):
			groups[key][1] += locs[arr[i]][1]
		groups[key][1] /= len(arr)
	#rank the zip codes
	temp_d = {}
	for key in groups:
		temp_d[key] = groups[key][1]
	iters = 0
	for key in sorted(temp_d, key=temp_d.get, reverse=False):
		iters += 1
		groups[key][2] = iters
	for key in groups:
		arr = groups[key][0]
		for i in range(len(arr)):
			ret[arr[i]] = [key,groups[key][1],groups[key][2]]
	return ret

#starts prog
def main():
	x = []
	y = []
	zips = []
	readInFiles()
	placeInLists(x,y,zips)
	print("Num points initially: ", len(x))
	#plotting.scatterBasic(x,y)
	x,y,roots,maxLen = superRemove(x,y,zips)
	print("Num points after super filter: ", len(x))
	#plotting.scatterBasic(x,y)
	filterLocs()
	x = []
	y = []
	zips = []
	placeInLists(x,y,zips)
	print("Num points after removing places with no commute times: ", len(x))
	#plotting.scatterBasic(x,y)
	#1. Cluster nodes into n (250 for now) groups based on k-means
	centers, preds, locs = ml.kmeans(k,iters,x,y,roots,maxLen)
	#plotting.plotCenter(centers)
	#plotting.plotScatterColor(locs,preds,k)
	#2. With these clusters, get the average commute time with all the zip codes
	zipInfoDict = getZipInfoDict(preds,locs,zips)
	#3. Rank them somehow... Maybe I can use the names from earlier? Or maybe some machine learning can come into play...
	interactWithUser(zipInfoDict)

main()