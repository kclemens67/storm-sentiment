import os
import sys

# points to Anaconda python packages installed on Ubuntu AWS

other_pythondir1 = '/home/ubuntu/anaconda2/lib/python2.7/site-packages/'
for root, dirs, files in os.walk(other_pythondir1):
	sys.path.append(root)

 # import python packages 

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
import statistics
from statistics import median, mean


@app.route('/')
@app.route('/index')

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/bad_output')

@app.route('/output')
def cesareans_output():
  #from sqlalchemy import create_engine
  #from sqlalchemy_utils import database_exists, create_database
  #import pandas as pd
  #import psycopg2
  #import numpy as np

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

  query = """SELECT date_stamp,location,org_text,temp,weather_rating,num_weather_words,norm_response_score, point(%s, %s) <@> point(long, lat)::point AS tweet_distance 
    FROM tweet_weather_table 
    WHERE (point(%s, %s) <@> point(long, lat)) < 10 
    ORDER by tweet_distance;""" %(query_lon,query_lat,query_lon,query_lat)

    # convert query to pd df
  query_results=pd.read_sql_query(query,con)

    # check to make sure pd df is not empty or not enough tweets
  if query_results.empty or len(query_results) < 10:
      print 'not enough tweets!'
      return render_template("bad_output.html")
    
    # get the negative and positive tweets and seperate into two lists
  neg_data = query_results.loc[query_results['norm_response_score'] < 0].sort_values('norm_response_score',axis = 0, ascending=True)
  pos_data = query_results.loc[query_results['norm_response_score'] > 0].sort_values('norm_response_score',axis = 0, ascending=False)

    # get the response scores for neg and pos and factor in num of weather words

  neg_data_scores = neg_data['norm_response_score']*neg_data['num_weather_words']
  pos_data_scores = pos_data['norm_response_score']*pos_data['num_weather_words']

    # normalize median values to number of tweets in each and take abs() 
  adj_median_neg = abs(median(neg_data_scores)*len(neg_data))
  adj_median_pos = median(pos_data_scores)*len(pos_data)


  if adj_median_neg > adj_median_pos:
      percent_diff = (adj_median_neg-adj_median_pos)/float(adj_median_neg+adj_median_pos)*-1
      
  if adj_median_neg < adj_median_pos:
      percent_diff = (adj_median_pos-adj_median_neg)/float(adj_median_neg+adj_median_pos)

  if adj_median_neg == adj_median_pos:
      percent_diff = 0
      

  percent_diff = percent_diff*100

    # get response scores and weather ratings for most negative tweets
  neg_weather_rating = [ x for x in neg_data['weather_rating']]

    # get response socres and weather ratings for most positive tweets
  pos_weather_rating = [ x for x in pos_data['weather_rating']]

    # calcuate aggregate weather rating 

  agg_weather_rating = int(np.sum(neg_weather_rating + pos_weather_rating))/int((len(neg_weather_rating)+len(pos_weather_rating)))


    # calculate average temp (should be about the same for all since around the same time/location)
  temp = [x for x in query_results['temp'].apply(int)]
  avg_temp = np.sum(temp)/len(temp)

    # get orginal tweet text body for neg and pos lists
  neg_tweets = [ x for x in neg_data['org_text']]
  pos_tweets = [ x for x in pos_data['org_text']]

    # clean up the language in the tweet body
  neg_censored_list = censor_tweets(neg_tweets)
  pos_censored_list = censor_tweets(pos_tweets)

    # get the dates for the tweets in neg and pos lists
  neg_dates = [x for x in neg_data['date_stamp']]
  pos_dates = [x for x in pos_data['date_stamp']]

    # representitive tweets 
  example_tweets_neg = neg_censored_list[:3]
  example_tweets_pos = pos_censored_list[:3]



  if int(percent_diff) < -75:
      description = 'extremely negative'

  if -75 <= int(percent_diff) < -50:
      description = 'very negative'

  if -50 <= int(percent_diff) < -25:
      description = 'negative'

  if -25 <= int(percent_diff) < 0:
      description = 'somewhat negative'

  if int(percent_diff) > 75:
      description = 'extremely positive'

  if 75 >= int(percent_diff) > 50:
      description = 'very positive'

  if 50 >= int(percent_diff) > 25:
      description = 'positive'

  if 25 >= int(percent_diff) > 0:
      description = 'somewhat positive'

  if int(percent_diff) == 0: 
      description = " neutral"

  print percent_diff
  print description
  print example_tweets_neg
  print example_tweets_pos

  the_result = avg_temp

  return render_template("output.html", query_results = the_result,agg_weather_rating=agg_weather_rating, response_score=percent_diff,example_tweets_pos=example_tweets_pos,example_tweets_neg=example_tweets_neg,description=description)
