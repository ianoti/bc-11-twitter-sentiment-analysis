import requests
from access_credentials import credentials
from stopwords import stopwords
import json
from progressbar import *
from requests_oauthlib import OAuth1
import sqlite3
import itertools
import sys
import sentiment_analysis
from time import sleep
from tabulate import tabulate
import re
from pyfiglet import Figlet

'''
# The authentication tokens are handled here
'''

auth = OAuth1(credentials["consumer_key"], credentials["consumer_secret"],
				credentials["access_token"], credentials["access_token_secret"])

'''
# The database is created here using sqlite3
'''

conn = sqlite3.connect("twitter_tweets.db")
conn.execute('''CREATE TABLE IF NOT EXISTS Twitter
			(TWEET_KEY text PRIMARY KEY NOT NULL,
			TWEET_SCREEN_NAME text NOT NULL,
			TWEET_CONTENT text NOT NULL,
			UNIQUE(TWEET_KEY,TWEET_CONTENT)
			);''')
conn.close()

'''
# This function holds the user interface for interaction with the program
'''
def interface():
	f = Figlet(font="slant")
	print(f.renderText("Twitter Semantic"))
	print("#"*70)
	print ("\n------------What do you want------------------",
		"\n1. Retrieve some tweets\n2. View saved users in system",
		"\n3. View the status of the authentication keys\n4. Delete all tweets of a user",
		"\n5. View emotional tone of tweets of user\n6. Count words in tweets of a user",
		"\n7. Perform sentiment analysis on tweets of user\n8. Exit the application\n",
		"\n9. (presentation purpose only) diplay user tweets as text\n")
	option = input("Please enter your choice: ")
	if option == "1":
		user_name = input("Please provide me with a twitter handle without the @ e.g oti_ian instead of @oti_ian\n")
		tweet_number = input("Please give the number of most recent tweets you want to receive\n")
		tweet_get(user_name,tweet_number)		
		interface()

	elif option == "2":
		tweet_print_all()
		interface()

	elif option == "3":
		authenticate_token()
		interface()

	elif option == "4":
		user_name = input("give the twitter handle of the user whose tweets you want to delete\n")
		remove_tweets(user_name)
		interface()

	elif option == "5":
		user_name = input("give the twitter handle of the user whose tweets you want to view emotions of\n")
		text_of_tweets = see_tweets(user_name)
		
		emotion_raw = sentiment_analysis.emotion_check(text_of_tweets)
		emotion_json = json.loads(emotion_raw)
		tweet_emotion = emotion_json["docEmotions"]
		formatted_view = sort(tweet_emotion)
		print(tabulate(formatted_view, headers=["emotions","probability of emotion occurrence"], tablefmt = "orgtbl"))
		
		interface()

	elif option == "6":
		user_name = input("give the twitter handle of the user whose tweets you want to word count\n")
		tweet_word_list_count = tweet_word_count(user_name)
		formatted_view = sort_word_freq(tweet_word_list_count)
		print(tabulate(formatted_view, headers=["word frequency", "word"], tablefmt = "fancy_grid"))
		interface()

	elif option == "7":
		user_name = input("give the twitter handle of the user whose tweets you want to view sentiment of\n")
		text_of_tweets = see_tweets(user_name)
		sentiment_raw = sentiment_analysis.tweet_sentiment(text_of_tweets)
		sentiment_json = json.loads(sentiment_raw)
		sentiment = sentiment_json["docSentiment"]
		formatted_view = sort(sentiment)
		print(tabulate(formatted_view, headers=["Sentiment measures", "Sentiment score", "sentiment type"], tablefmt = "fancy_grid"))
		interface()

	elif option == "8":
		print("The program has closed, Bye Bye")
		exit()

	elif option == "9":
		user_name = input("give the twitter handle of the user whose tweets you want to view as text\n")
		text_of_tweets = see_tweets(user_name)
		print("the tweets of:", user_name, "are:", text_of_tweets)
		interface()

	else:
		print("I don't understand what you want, I'm limited in my choices go back and choose again")
		interface()

'''
#This function retrieves tweets of a specified user of a specified number of tweets
'''
def tweet_get(user_name, tweet_number):
	url_tweets = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user_name+"&count="+tweet_number+""
	tweet = requests.get(url_tweets, auth=auth)
	chunk = 1
	i = 0
	'''
	# the progressbar uses iter_content() to calculate how long to return
	'''
	bar = progressbar.ProgressBar(maxval=(len(list(tweet.iter_content())))).start()
	with open("tweet.txt", "w") as outfile:
		for chunk in tweet.iter_content():		
			outfile.write(chunk.decode("utf-8"))
			bar.update(i)
			i += 1	
	bar.finish()

	with open("tweet.txt") as output_file:
			data = output_file.read()

	tweet_json = json.loads(data)

	with open("tweet.json", "w") as json_file:
			json.dump(tweet_json, json_file, indent = 4, sort_keys = True)
	
	for i in range(0,len(tweet_json)):
		try:
			conn = sqlite3.connect("twitter_tweets.db")
			tweet_user = tweet_json[i]["user"]["screen_name"]
			tweet_id = tweet_json[i]["id_str"]
			tweet_text = tweet_json[i]["text"]
			tweet_textenc = tweet_text.encode("utf-8", "ignore") #this encodes the text as utf-8 as is received from Twitter
			conn.execute("INSERT OR IGNORE INTO Twitter(TWEET_KEY, TWEET_SCREEN_NAME, TWEET_CONTENT) VALUES(?, ?, ?);", (tweet_id, tweet_user, tweet_textenc))
			conn.commit()
			conn.close()
		except (KeyError,TypeError):
			print("there's a problem with the data you provided, please confirm it's accurate and in the expected format")
			interface()
	
'''
# This function prints out all the archived tweets in the database
'''
def tweet_print_all():
	conn = sqlite3.connect("twitter_tweets.db")
	cursor = conn.execute("SELECT TWEET_SCREEN_NAME, COUNT(*) FROM Twitter GROUP BY TWEET_SCREEN_NAME ORDER BY TWEET_SCREEN_NAME")
	table = cursor.fetchall()
	print (tabulate(table, headers=["Saved handles","Stored tweets"], tablefmt="fancy_grid"))
	conn.close()

'''
# This function confirms the authentication of the access tokens
'''
def authenticate_token():
	url_authenticate = "https://api.twitter.com/1.1/account/verify_credentials.json"
	auth_status = requests.get(url_authenticate, auth=auth)
	if auth_status.status_code == 200:
		print ("The access codes are still valid")
	

'''
# this function deletes archived tweets matching a user name
'''
def remove_tweets(user_name):
	conn = sqlite3.connect("twitter_tweets.db")
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Twitter WHERE TWEET_SCREEN_NAME=:who", {"who": user_name})
	conn.commit()
	conn.close()

'''
# this function will return the tweets saved from a particular user
'''
def see_tweets(user_name):
	conn = sqlite3.connect("twitter_tweets.db")
	cursor = conn.cursor()
	cursor.execute("SELECT TWEET_CONTENT FROM Twitter WHERE TWEET_SCREEN_NAME=:who", {"who": user_name})
	tweet_holder = cursor.fetchall()
	user_tweets = list(itertools.chain(*tweet_holder))
	user_tweet_text = b" ".join(user_tweets) #the stuff in database is stored as byte string, this code strings all the tweets together
	user_tweet_english = user_tweet_text.decode("utf-8")
	conn.close()
	return str(user_tweet_english)

'''
# this function will count the number of words in the tweet
'''
def tweet_word_count(user_name):
	text_of_tweets = see_tweets(user_name)
	text_of_tweets_normalised = text_of_tweets.lower()
	tweet_words = removeNonAlphaNum(text_of_tweets_normalised)
	reduced_tweet = remove_stop_words(tweet_words, stopwords)
	count_of_words_in_tweet = {}
	for some_text in reduced_tweet:
		if some_text in count_of_words_in_tweet:
			count_of_words_in_tweet[some_text] += 1
		else:
			count_of_words_in_tweet[some_text] = 1
	return count_of_words_in_tweet

'''
# this function will clean up the tweets to remove arbitrary punctuation and replace with whitespace
'''
def removeNonAlphaNum(text_of_tweets_normalised):
	return re.sub("[, ( ) ]", " ", text_of_tweets_normalised)

'''
# This function removes the stop words using a list stored in separate file
'''
def remove_stop_words(tweet_words, stopwords):
	individual_words = tweet_words.split()
	return [w for w in individual_words if not (w in stopwords)]

'''
# This pair of  functions accepts a dictionary or list and sorts the keys
# the function is called depending on whether sorting is done by key or value
'''
def sort(some_list):
	aux = [(key, some_list[key]) for key in some_list]
	aux.sort()
	aux.reverse()
	return aux
def sort_word_freq(some_list):
	aux = [(some_list[key], key) for key in some_list]
	aux.sort()
	aux.reverse()
	return aux
'''
# The User interface is initialised and program
# begins execution
'''

interface()