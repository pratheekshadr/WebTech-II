
import pickle
import csv
import pandas as pd
import os
import random
from sklearn.utils import shuffle
import numpy as np
from math import cos, asin, sqrt


#reading the saved model form pickle file
pickle_in = open("static/knn/knn.pickle","rb")
model = pickle.load(pickle_in)

indices = model['indices']
address = model['address']
#finding k nearest neighbors
k = 10


#file ith information about places and their latitude, longitude
global searchdf
searchdf = pd.read_csv("static/datasets/latlong.csv") 

#function that finds nearest points to the place passed as parameter
#returns a list of nearest places
def getNeighbors(place):
	place_index = address.index(place)
	nearest_places = []
	
	#reading the nearest points index from precomputed indices 
	#and finding the actual place name from the index
	for i in range(1,k):
		index = indices[place_index,i]
		nearest_places.append(address[index])
	return nearest_places

#function to get the latitude and longitude of a place passed as parameter
def find_lat_long(place):
	global searchdf
	row = searchdf.loc[searchdf['address']== place ]
	return (row.latitude, row.longitude)
	
#function to calculate fare from one place to another 
#given latitude and longitude of both the points by using haversine distance between them
def getFare(lat1, long1, lat2, long2, seats):
	p = 0.017453292519943295   
	a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((long2 - long1) * p)) / 2
	dist = 12742 * asin(sqrt(a))
	print(dist)
	fare = ( dist * 5 ) // seats
	#print(dist, seats, fare)
	return fare


def getPlaces():
	source = form.get['source']
	seats = form.get['seats']
	destination = form.get['destination']
	#destination = form.get['destination']
	#source = 'AJJAMPURA,TARIKERE,CHICKMAGALUR,KARNATAKA'
	#destination = 'BELLANDUR,BANGALORE SOUTH,BANGALORE,KARNATAKA'

	souce_npalces = getNeighbors(source)
	fare = []
	#destination_nplaces = getNeighbors(destination)
	
	#calculating the fare from nearest pickup points to destination 
	lat1, long1 = find_lat_long(destination)
	for place in source_nplaces:
		lat2, long2 = find_lat_long(place)
		fare.append(getFare(lat1, long1, lat2, long2))
		
	#value to be retuned to the client
	#format: [[place1, fare1],[place2, fare2], .....]
	pickupPoints = []
	for i in range(k):
		pickupPoints.append([souce_npalces[i], fare[i])
	
	return render_template("offer_page.html", pickupPoints = pickupPoints)