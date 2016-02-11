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
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib
import math


@app.route('/')
@app.route('/index')

@app.route('/input')
def cesareans_input():
    return render_template("input.html")

@app.route('/bad_output')

@app.route('/output')
def cesareans_output():

  def postgres_connect():
    conn_string = "host='localhost' dbname='final_db' user='root'"
    print "Connecting to database\n ->%s" % (conn_string)
    conn = psycopg2.connect(conn_string)
    return() 

  def censor_tweets(tweet_list):
    bad_word_list = ['fuck','fucking','shit','ass','dick','bitch',"Fuck",
                     'Fucking','Shit',"Ass","Dick","Bitch",'Damn',"damn"]
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
      

  percent_diff = float(percent_diff)*100

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

  if percent_diff < 0:
    example_tweets_1 = neg_censored_list[:3]
    example_tweets_2 = pos_censored_list[:3]
    example_statement_2 = 'Positive'
    example_statement_1 = 'Negative'
    example_color_2 = 'color:Blue;'
    example_color_1 = 'color:red;'

  if percent_diff >= 0:
    example_tweets_2 = neg_censored_list[:3]
    example_tweets_1 = pos_censored_list[:3]
    example_statement_1 = 'Positive'
    example_statement_2 = 'Negative'
    example_color_1 = 'color:Blue;'
    example_color_2 = 'color:red;'

  if float(percent_diff) < -80:
      description = 'extremely negative'

  if -80 <= float(percent_diff) < -40:
      description = 'very negative'

  if -40 <= float(percent_diff) < -20:
      description = 'negative'

  if -20 <= float(percent_diff) < 0:
      description = 'somewhat negative'

  if float(percent_diff) > 80:
      description = 'extremely positive'

  if 80 >= float(percent_diff) > 40:
      description = 'very positive'

  if 40 >= float(percent_diff) > 20:
      description = 'positive'

  if 20 >= float(percent_diff) > 0:
      description = 'somewhat positive'

  if float(percent_diff) == 0: 
      description = " neutral"



  def make_colormap(seq):
      """Return a LinearSegmentedColormap
      seq: a sequence of floats and RGB-tuples. The floats should be increasing
      and in the interval (0,1).
      """
      seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
      #print seq
      #print list(seq)
      cdict = {'red': [], 'green': [], 'blue': []}
      for i, item in enumerate(seq):
          #print i, item
          if isinstance(item, float):
              r1, g1, b1 = seq[i - 1]
              r2, g2, b2 = seq[i + 1]
              cdict['red'].append([item, r1, r2])
              cdict['green'].append([item, g1, g2])
              cdict['blue'].append([item, b1, b2])
      return mcolors.LinearSegmentedColormap('CustomMap', cdict)


  c = mcolors.ColorConverter().to_rgb
  rvb = make_colormap(
      [c('red'), c('violet'), 0.50, c('violet'), c('blue')])

  def find_color_value(x):
      min_val = -100
      max_val = 100

      my_cmap = cm.get_cmap(rvb) # or any other one
      norm = matplotlib.colors.Normalize(min_val, max_val) # the color maps work for [0, 1]

      x_i = x
      color_i = my_cmap(norm(x_i)) # returns an rgba value
      return(color_i)

  test1,test2,test3,test4= find_color_value(int(percent_diff))

  rgb_color= 'color:rgb(%s,%s,%s);' %(int(math.floor(test1*255)),int(math.floor(test2*255)),int(math.floor(test3*255)))
  
  the_result = avg_temp

  return render_template("output.html",location=loc_input, query_results = the_result,agg_weather_rating=agg_weather_rating, response_score=percent_diff,example_tweets_pos=example_tweets_pos,example_tweets_neg=example_tweets_neg,description=description,customRGB=rgb_color,example_tweets_1=example_tweets_1,example_tweets_2=example_tweets_2,example_statement_1=example_statement_1,example_statement_2=example_statement_2,exampleColOne=example_color_1,exampleColTwo=example_color_2)
