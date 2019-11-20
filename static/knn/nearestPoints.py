from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd

def distance(p1, p2):
    lon1, lat1 = p1
    lon2, lat2 = p2
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

	
col_names = ['address','latitude','longitude']
data = pd.read_csv("C:/Users/prath/Desktop/WebTechProject/places.csv", header=None, names=col_names)

data = data.to_dict('records')


points = [[x['latitude'], x['longitude']] for x in data]
address = [x['address'] for x in data] 

k = 20
print("training....")
nbrs = NearestNeighbors(n_neighbors=k, metric=distance).fit(points)
print("finding nearest neighbors...")
distances, indices = nbrs.kneighbors(points)

print("creating pickle file")
import pickle
model = {'indices':indices,'distances':distances,'address':address}
pickle_out = open("static/knn/knn.pickle","wb")
pickle.dump(model, pickle_out)
pickle_out.close()

print("opening pickle file")
pickle_in = open("static/knn/knn.pickle","rb")
model = pickle.load(pickle_in)

indices = model['indices']
address = model['address']
for i in range(1,k):
	#nearest neighbor to the point in 0th index is the point at ith index
	print(indices[0,i])
	print(address[i])
	
	
