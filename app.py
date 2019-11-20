from flask import Flask, render_template, request, json,session, redirect
from flask_pymongo import PyMongo
from flask_cors import CORS

import pickle
import csv
import pandas as pd
import os
import random
from sklearn.utils import shuffle
import numpy as np
from math import cos, asin, sqrt
import json
import time
decrease_seats=0

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
	for i in range(1,k+1):
		index = indices[place_index,i]
		nearest_places.append(address[index])
	return nearest_places

#function to get the latitude and longitude of a place passed as parameter
def find_lat_long(place):
    global searchdf
    
    row = searchdf.loc[searchdf['address']== place ]
    row = row.values.tolist()
    row = row[0]
    
    lat = row[1]
    long1 = row[2]
    return (lat, long1)
    #return (row.latitude, row.longitude)
	
#function to calculate fare from one place to another 
#given latitude and longitude of both the points by using haversine distance between them
def getFare(lat1, long1, lat2, long2, seats, cost_km):
    seats = int(seats)
    cost_km = int(cost_km)

    p = 0.017453292519943295   
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((long2 - long1) * p)) / 2
    dist = 12742 * asin(sqrt(a))
    fare = ( dist * cost_km ) // seats
    #print(dist, seats, fare)
    return fare



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/wt"
mongo = PyMongo(app)
app.secret_key = "any random string"
CORS(app)

# @app.route('/')
# def hello():
#     return "Hello World!"
@app.route('/home')
def home():
    session['logged_in']=False
    return render_template('main2.html')


@app.route('/index')
def index():
    print(session['username'])
    return render_template('index.html')
     
@app.route('/stream')
def stream():         
    res=[]
    s=mongo.db.sse.find({});
    for t in s:
        res.append(t)
    newlist=sorted(res, key = lambda k:k['count'], reverse=True)

    Row_list=[]
    for i in range(0,2):
        Row_list.append(newlist[i]);
    print(Row_list)
    return render_template('cometSSE.html',output=Row_list)

@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

@app.route('/signUp/signUpUser', methods=['POST'])
def signUpUser():
    session['logged_in'] = True
    search_signup = []
    username =  request.form['username']
    
    search=mongo.db.users.find({"username":username})

    for doc in search:
        search_signup.append(doc)

    password  = request.form['password']
    email     = request.form['email']
    telephone =request.form['telephone']
    session['username'] = username
    if search_signup == []:
            session['username'] = username
            mongo.db.users.insert({'username':username,'password':password,'email':email,'telephone':telephone})
            print(session['logged_in'])
            print(session['username'])
            return redirect("/index")
            # return json.dumps({'status':'New user created'});
    else:
            # ?????? where will this go???     alert that user already exists and redirect to signup page itself
            # return render_template('signUp.html',data="user exists")  
            return json.dumps({'status':'User already exists'})
            #return redirect("/index")


@app.route('/offerRidePage/getPlaces/<string:term>', methods=["GET"])
def getPlaces(term=None):
    pattern = (term.split('='))[1]

    matching_lines = [line.rstrip("\n") for line in open('static/datasets/places.txt').readlines() if pattern in line]
    
    #if more than 20 places match, return first 20 places
    if(len(matching_lines)>20):
        matching_lines = matching_lines[:20]
    return json.dumps(matching_lines)

@app.route('/offerRidePage/knn/<string:term>', methods=["GET"]) 
def knn(term=None):
    places = (term.split('='))[1]
    placesArr = places.split(';')
    offer_source = placesArr[0]
    offer_dest = placesArr[1]
    offer_seats = placesArr[2]
    cost_km = placesArr[3]

    souce_nplaces = getNeighbors(offer_source)
    fare = []

    #calculating the fare from nearest pickup points to destination 
    coord = find_lat_long(offer_dest)
    lat1 = pd.to_numeric(coord[0])
    long1 =  pd.to_numeric(coord[1])
    for place in souce_nplaces:
        coord= find_lat_long(place)
        lat2 = pd.to_numeric(coord[0])
        long2 =  pd.to_numeric(coord[1])


        fare.append(getFare(lat1, long1, lat2, long2, offer_seats, cost_km))
        
    #value to be retuned to the client
    #format: [[place1, fare1],[place2, fare2], .....]
    pickupPoints = []
    for i in range(10):
        cost = fare[i]
        if not(cost):
            cost = 50.0
        pickupPoints.append([souce_nplaces[i], cost]) 
    print(json.dumps(pickupPoints))
    return json.dumps(pickupPoints)

@app.route('/login')
def login():
    print("login")
    return render_template('login.html')


@app.route('/login/loginUser',methods=['POST'])
def loginUser():
    if session.get('logged_in'):
        print(session['username'])
        print("already logged in")
        return redirect("/index")

    uname = request.form['uname_login']
    pwd   = request.form['pwd_login']
    search_res = []
    search=mongo.db.users.find( { "$and": [ {"username":uname}, {"password":pwd} ] } )
    for doc in search:
        search_res.append(doc)
        print(doc)
    # print(search_res);
    # print(search);
    if search_res==[]:
        print("Invalid credentials")
        return json.dumps({'status':"Invalid"})

        #????redirect to which page     alert invalid credentials and redirect to login page
        # return render_template("login.html")
    else:
        print("successfully logged in")
        session['logged_in'] = True
        session['username']  = uname
        # return json.dumps({'status':'logged in'});
        return redirect("/index")
    

@app.route("/logout")
def logout():
    print(session['logged_in'])
    session['logged_in'] = False
    session['username']  =""
    print(session['logged_in'])
    print(session['username'])
    return redirect("/home")    ##redirect to homepage


@app.route('/offer')
def offer():
    if session.get('logged_in'):
        return redirect("/offerRidePage")
    else:
        # return json.dumps({'status':"Login First"});
        return redirect("/login")

@app.route('/offerRidePage')
def offerRidePage():
    return render_template('offer.html')

@app.route('/offerRide',methods=['POST'])
def offerRide():
    arr = []
    uname = session['username']
    search = mongo.db.users.find({"username":uname} )
    for term in search:
        arr.append(term)
    email=arr[0]['email']
    phno=arr[0]['telephone']
  
    offer_source = request.form['offer_source']
    offer_dest   = request.form['offer_dest']
    offer_seats  = int(request.form['offer_seats'])
    cost_km      = request.form['cost_km']
    offer_pickupPoints  = request.form['offer_pickuppoints']

    # print("\n\n\n\n********")
    print(offer_seats)
    car_model  = request.form['car_model']
    reg_no     =request.form['reg_no']
    offer_date =request.form['offer_date']
    offer_time =request.form['offer_time']

    mongo.db.offer.insert({'username':uname,'email':email,'phno':phno,'offer_source':offer_source,'offer_dest':offer_dest,
        'car_model':car_model,'reg_no':reg_no,'offer_seats':offer_seats,
        'cost_km':cost_km,'offer_date':offer_date,'offer_time':offer_time,
        'pickUpPoints':offer_pickupPoints});
    print("Offered ride confirmed")

    return redirect('/home')


  
@app.route('/join')
def join():
    if session.get('logged_in'):
        return redirect("/joinRidePage")
    else:
        # return json.dumps({'status':"Login First"});
        return redirect("/login")

@app.route('/joinRidePage')
def joinRidePage():
    return render_template('join.html')

@app.route('/joinRide',methods=['POST'])
def joinRide():
    global decrease_seats
    # print(decrease_seats)
    arr_details  = []
    available_rides = []

    uname = session['username']
    search = mongo.db.users.find({"username":uname} )

    for term in search:
        arr_details.append(term)

    email = arr_details[0]['email']
    phno = arr_details[0]['telephone']
    join_source = request.form['join_source']
    join_dest = request.form['join_dest']
    join_seats = int(request.form['join_seats'])
    join_date = request.form['join_date']
    decrease_seats=join_seats
    # print(decrease_seats)
    # join_time=request.form['join_time']
    # print(arr_details)
    # print(arr_details[0])
    # print(arr_details[0]['_id'])

    print("\n\n***************")
    print(join_source)
    print(join_dest)
    search_avail=mongo.db.offer.find( { "$and": [ {"offer_source":join_source}, {"offer_dest":join_dest}] } );
    print(search_avail)
    for term in search_avail:
        print(term)
        available_rides.append(term)
    # print(available_rides)
    # print(len(available_rides))
    
    print(available_rides)
    return render_template("join_avail.html",data=available_rides)
    # return json.dumps({'status':"query ride"});

@app.route('/updateRecords',methods=['POST','GET'])
def updateRecords():
    global decrease_seats
    print("update")
    print(decrease_seats)
    upd_arr=[]
    sse_arr=[]
    sel_radio=request.form['radio_join']
    strr=str(decrease_seats-1)
    # print(sel_radio)
    # mongo.db.offer.update( { "username": sel_radio },{ "$inc": { "offer_seats": strr } })
    decrease_seats=0

    print("updateeeee")
    print(decrease_seats)
    rec=mongo.db.offer.find( { "$and": [ {"username":sel_radio}] } );
    for x in rec:
        upd_arr.append(x)
    upd_source=upd_arr[0]['offer_source']
    upd_dest=upd_arr[0]['offer_dest']

    sse_search=mongo.db.sse.find( { "$and": [ {"source":upd_source},{"destination":upd_dest}] } );
    for y in sse_search:
        sse_arr.append(y)
    # print(sse_arr)
    if sse_arr==[]:
        mongo.db.sse.insert({'source':upd_source,'destination':upd_dest,'count':1});
    else:
        mongo.db.sse.update( { "$and": [ {"source":upd_source},{"destination":upd_dest}] },{ "$inc": { "count": 1 } })

    ##alert and redirect to home page
    # return json.dumps({'Confirmation':"Hurray! Your ride is booked"});
    return redirect('/home')

@app.route('/writeCSV')
def writeCSV():
    a=[]
    rec=mongo.db.sse.find({});
    for x in rec:
        a.append(x)
    with open('test_output.csv', 'w') as csvfile:
        fields = ['source','destination','count']
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for x in a:
            writer.writerow({'source':x["source"],'destination': x["destination"],'count':x["count"]});
    return json.dumps({"a":"a"});


if __name__=="__main__":

    app.run()
