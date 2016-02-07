# import modules for gatherigng tweets and weather data
import datetime
import json
import time
import numpy
import os
import pyowm
import re
import sys
import tweepy

# set time for saving files
time = datetime.datetime.now().strftime("%y%m%d%s")

# Authentication details
# Authentication keys for Twitter API
consumer_key = "Po4DjalaCYX3OLNKRmvGtT8Of" 
consumer_secret = "cOFRchBACeJtJ1V1r5PjmNJ6PQADa38viJbsRDG5GvDNYsvsAY"
access_token = "4759540993-iiq5TsgYXwNBCsdmgu1TnS6ZugysAV0ZM9pWhI8"
access_token_secret = "m1NPnLqRSJ4NXFZQK9moerwEVb8YhLnoyLWqc1kx6r2xx" 

# API key for open weather map API

API_key = '6922b2f55edba960585b0f0c38aa17dd'
owm = pyowm.OWM(API_key)


tweet_file = open("%s_tweet_list.txt" % time,'wa')
term_file = open("%s_term_list.txt" % time,'wa')
weather_file  = open("%s_weather_list.txt" % time,'wa')
# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        if 'text' and 'place' in decoded:
            tweet = json.loads(data)['text']
                    
            search_terms = ['Rain',' rain ','raindrops',' raining','Raining','Snow','snow',' Sun ',' sun ',
                            'Sunny','sunny','Cloud','cloud','Monsoon',
                            'monsoon','Thunder','thunder','Blizzard','blizzard',
                            'Icey','icey','warm weather',
                            'hot weather','cold weather','Warm weather',
                            'Hot weather','Cold weather',
                            'Rain showers','rain showers','flash flood',
                            'Flash flood','stormy weather','Fog',' fog ']
            for term in search_terms:
                if term in json.loads(data)['text']:
                    print tweet
                    print term
                    coordinates = decoded['place']['bounding_box']['coordinates']
                    print decoded['place']
                    coord3= coordinates[0][0][0]
                    coord1= coordinates[0][0][1]
                    coord2 = coordinates[0][1][1]
                    coord4 = coordinates[0][2][0]
        
                    coords = (coord1,coord2,coord3,coord4)       
        
                    centerx,centery = (numpy.average(coords[:2]),numpy.average(coords[2:]))
                    location = decoded['place']['full_name']
                    print location
                    print float(centerx),float(centery)

                    
                    observation = owm.weather_around_coords(float(centerx),float(centery),limit=1)
                    for obs in observation:
                        w = obs.get_weather()
                        weather_status_detailed= str(w.get_detailed_status())
                        rain_status= str(w.get_rain())
                        snow_status = str(w.get_snow())
                        clouds = str(w.get_clouds())
                        wind = str(w.get_wind())
                        humidity = str(w.get_humidity())
                        temp = str(w.get_temperature())
                        weather_status= str(w.get_status())
                        weather_code = str(w.get_weather_code())
                        weather_icon = str(w.get_weather_icon_name())
                        new_line = [weather_status_detailed,weather_status,weather_code,weather_icon,rain_status,snow_status,clouds,wind,humidity,temp]
                       
                        print new_line 

                    tweet_file.writelines(data)
                    term_file.writelines(term+"\n")
                    weather_file.writelines("\t".join(new_line)+"\n")
                        
                        
        else:
            pass
        
            

        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    print "Showing all new tweets for weather related terms:"

    # There are different kinds of streams: public stream, user stream, multi-user streams
    # In this example follow #programming tag
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    stream = tweepy.Stream(auth, l)
    stream.filter(locations=[-127.441,24.087,-79.761,49.582])
