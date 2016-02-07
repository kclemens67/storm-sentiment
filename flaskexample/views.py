import os
import sys

# points to Anaconda python packages installed on Ubuntu AWS

other_pythondir1 = '/home/ubuntu/anaconda2/lib/python2.7/site-packages/'
for root, dirs, files in os.walk(other_pythondir1):
	sys.path.append(root)

from flask import render_template
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from flask import request
import re
import csv
import json
import numpy as np
import regex
import nltk.classify
from geopy.geocoders import Nominatim, GoogleV3

@app.route('/')
@app.route('/index')

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/bad_output')

@app.route('/output')
def cesareans_output():
  from sqlalchemy import create_engine
  from sqlalchemy_utils import database_exists, create_database
  import pandas as pd
  import psycopg2
  import numpy as np

  def postgres_connect():
    conn_string = "host='localhost' dbname='final_db' user='root'"
    print "Connecting to database\n ->%s" % (conn_string)
    conn = psycopg2.connect(conn_string)
    return() 

  def censor_tweets(tweet_list):
    bad_word_list = ['fuck','fucking','shit','ass','dick','bitch']
    censored_list = []
    for item in tweet_list:
      for x in bad_word_list:
          item = item.replace(x,"@#$%!")
      censored_list.append(item)
    return censored_list

  user = 'root' #add your username here (same as previous postgreSQL)            
  host = 'localhost'
  dbname = 'final_db'
  db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
  con = None
  con = psycopg2.connect(database = dbname, user = user)

  loc_input = request.args.get('location')

  geolocator = GoogleV3(api_key='AIzaSyB7LvwvLJN0l04rFfHbIyUBsqi61vP6qWA')

  query_address = loc_input

  geolocator = Nominatim()
  location = geolocator.geocode(query_address)
  query_lat = location.latitude
  query_lon = location.longitude

  query = """SELECT date_stamp,location,org_text,temp,weather_rating,norm_response_score, point(%s, %s) <@> point(long, lat)::point AS tweet_distance FROM tweet_weather_table WHERE (point(%s, %s) <@> point(long, lat)) < 10 ORDER by tweet_distance;""" %(query_lon,query_lat,query_lon,query_lat)

  query_results=pd.read_sql_query(query,con)

  if query_results.empty:
      print 'oops!'
      return render_template("bad_output.html")
  
  neg_data = query_results.sort_values('norm_response_score',axis = 0, ascending=True)
  pos_data = query_results.sort_values('norm_response_score',axis = 0, ascending=False)

  if len(neg_data) and len(pos_data) < 10:
    print 'not enough tweets'
    return render_template("bad_output.html")

  neg_data = neg_data[:10]
  pos_data = pos_data[:10]

  neg_response_score = neg_data['norm_response_score']
  neg_weather_rating = [ x for x in neg_data['weather_rating']]

  pos_response_score = pos_data['norm_response_score']
  pos_weather_rating = [ x for x in pos_data['weather_rating']]

  agg_weather_rating = int(np.sum(neg_weather_rating + pos_weather_rating))/20

  print neg_weather_rating, "neg weather rating"
  print pos_weather_rating, "pos weather rating"

  print agg_weather_rating, "agg weather rating"

  response_score = [x for x in neg_data['norm_response_score'].apply(int)]+[x for x in pos_data['norm_response_score'].apply(int)]

  #print response_score
  agg_response_score = int(np.sum(response_score))

  temp = [x for x in neg_data['temp'].apply(int)]+[x for x in pos_data['temp'].apply(int)]
  avg_temp = np.sum(temp)/len(temp)


  neg_tweets = [ x for x in neg_data['org_text']]
  pos_tweets = [ x for x in pos_data['org_text']]

  
  neg_censored_list = censor_tweets(neg_tweets)

    
  pos_censored_list = censor_tweets(pos_tweets)
    

  neg_dates = [x for x in neg_data['date_stamp']]
  pos_dates = [x for x in pos_data['date_stamp']]


  #avg_response_score = np.sum(response_score)/len(response_score)
  if int(agg_response_score) < 0:
    example_tweet = neg_censored_list[:5]
    example_score = neg_response_score
    print example_tweet

  if int(agg_response_score) > 0: 
    example_tweet = pos_censored_list[:5]
    example_score = pos_response_score
    print example_tweet
  if int(agg_response_score) == 0: 
    example_tweet = "This place is pretty neutral about the current weather"
    example_score = 0
    descriptiont = "neutral"
 
  if 10 > agg_response_score > 1:
    description = " positive"

  if agg_response_score > 10:
    description = " very positive"

  if -5 < agg_response_score < 0:
    description = " negative"

  if agg_response_score < -5:
    description = " very negative"

  the_result = avg_temp

  agg_response_score = ' '

  return render_template("output.html", query_results = the_result,agg_weather_rating=agg_weather_rating, response_score=agg_response_score,example_score=example_score,example_tweet=example_tweet,description=description)
