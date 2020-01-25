#!/usr/bin/env python
# coding: utf-8

# In[8]:


# Importing the required libraries for creating Flask based api
import flask
import json
from flask import request,jsonify
from geopy.distance import great_circle,geodesic


# In[12]:


# Reading the json file
with open("restaurants.json",'r') as fh:
    fileContent=json.load(fh)


# In[13]:


# Creating Flask instance
app=flask.Flask(__name__)
app.config["DEBUG"]=True


# In[9]:


# Mapping Url to function using route
@app.route("/",methods=["GET"])
def file_contents():
    ''' Returns the contents of json file'''
    return fileContent
restname=[]

@app.route("/restaurants",methods=["GET"])
def return_restaurantsname():
    '''Returns the listed restaurants name in data'''
    for restaurants in fileContent["restaurants"]:
        restname.append(restaurants["name"])
    return jsonify({"restname":restname})

@app.route('/restaurants/search', methods=['GET'])
def matched_resturants():
    '''Returns the most relevant restaurants within 3 km distance range'''
    # Fetching arguments as q:resturant hint, lat,lon: geolocation provided
    q= request.args.get('q', None)
    lat= request.args.get('lat', None)
    lon = request.args.get('lon', None)
    restaurants_in_range={}
    # Converting case to lower to q and tokens variable make case-insensitive
    # Variable q contains string parameter from query
    q=q.lower().split(" ")
    
    for restaurants in fileContent["restaurants"]:
        # Variabe tokens contains all the string information from resaturant name,description and tags
        tokens=[]
        description=restaurants["description"].split(" ")
        name=restaurants["name"].split(" ")
        tokens=restaurants["tags"]+description+name
        tokens=[x.lower() for x in tokens]
        lo,la=restaurants['location']
        # Calculating the distance between query location to all restaurants geolocations
        dist=great_circle((la,lo),(lat,lon)).km
        
        # Jaccard similarity approach to score the query string and the restuarnts name,description and tags informations
        js_score=len(set(q).intersection(set(tokens)))/len(set(q).union(set(tokens)))
 
        # Saving the resaurants whose js_score is greater than zero and distance from query(lat,lon) is within 3 km range
        if js_score>0.0 and (dist<3):
            restaurants_in_range[restaurants['name']]=js_score
            
    #sorting based upon jaccard similarity score
    matches=sorted(restaurants_in_range.items(),key=lambda t: t[1],reverse=True)
    return jsonify({"matched_restaurants":matches})

app.run()

