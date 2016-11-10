import requests
from access_credentials import credentials
from stopwords import stopwords
import json
from tqdm import tqdm
from requests_oauthlib import OAuth1
import sqlite3
import itertools
import sys
import sentiment_analysis
from time import sleep
from tabulate import tabulate

#----------------------
# The authentication tokens are handled here
#-----------------------

auth = OAuth1(credentials["consumer_key"], credentials["consumer_secret"],
				credentials["access_token"], credentials["access_token_secret"])

#--------------------------
# The database is created here using sqlite3
#--------------------------

conn = sqlite3.connect("twitter_tweets.db")
conn.execute('''CREATE TABLE IF NOT EXISTS Twitter
			(TWEET_KEY text PRIMARY KEY NOT NULL,
			TWEET_SCREEN_NAME text NOT NULL,
			TWEET_CONTENT text NOT NULL,
			UNIQUE(TWEET_KEY,TWEET_CONTENT)
			);''')
conn.close()

#----------------------------
# This function holds the user interface for interaction with the program
#----------------------------
def interface():
	print ("\nWhat do you want\n1. Retrieve some tweets\n2. View all archived tweets\n3. View the status of the authentication",
		"\n4. Delete all tweets of a user\n5. View tone of tweets of user\n6. Count words in tweets of a user"
		"\n9. Exit the application\n")
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
		user_name = input("give the twitter handle of the user whose tweets you want to view\n")
		text_of_tweets = see_tweets(user_name)
		#-------------------------------------------------------------
		emotion_raw = sentiment_analysis.emotion_check(text_of_tweets)
		emotion_json = json.loads(emotion_raw)
		s_emotion = emotion_json["docEmotions"]
		aux = [(key, s_emotion[key]) for key in s_emotion]
		aux.sort()
		aux.reverse()
		print(tabulate(aux, headers=["emotions","probability of emotion in tweet"], tablefmt = "fancy_grid"))
		
		interface()

	elif option == "6":
		user_name = input("give the twitter handle of the user whose tweets you want to word count\n")
		tweet_word_list_count = tweet_word_count(user_name)
		# print(tweet_word_list_count) # the tweets have been broken up into a list of words with punctuations eliminated and stop words removed
		
		aux = [(tweet_word_list_count[key], key) for key in tweet_word_list_count]
		aux.sort()
		aux.reverse()
		print(aux)
		interface()
		
	elif option == "9":
		print("The program has closed, Bye Bye")
		exit()

#--------------------------------
# This function retrieves tweets of a specified user of a specified number of tweets
#--------------------------------
def tweet_get(user_name, tweet_number):
	url_tweets = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user_name+"&count="+tweet_number+""
	tweet = requests.get(url_tweets, auth=auth)
	file_size = int(tweet.headers["content-length"])
	chunk = 1
	num_bars = file_size/chunk
	with open("tweet.txt", "w") as outfile:
		for chunk in tweet.iter_content():			
				outfile.write(chunk.decode("utf-8"))
				# sys.stdout.write("\r---%s" %i)
				# sys.stdout.flush()
				# sys.stdout.write("\b")
		for i in tqdm(range(len(list(tweet.iter_content())))):
			# for chunk in tweet.iter_content():
			# 	outfile.write(chunk.decode("utf-8"))
			sleep(0.000001)
				

	with open("tweet.txt") as output_file:
			data = output_file.read()
#------------------------------------------------------------------------------
	tweet_json = json.loads(data)

	with open("tweet.json", "w") as json_file:
			json.dump(tweet_json, json_file, indent = 4, sort_keys = True)

	conn = sqlite3.connect("twitter_tweets.db")
	for i in range(0,len(tweet_json)):
		tweet_user = tweet_json[i]["user"]["screen_name"]
		tweet_id = tweet_json[i]["id_str"]
		tweet_text = tweet_json[i]["text"]
		tweet_textenc = tweet_text.encode("utf-8", "ignore") #this encodes the text as utf-8 as is received from Twitter
		conn.execute("INSERT OR IGNORE INTO Twitter(TWEET_KEY, TWEET_SCREEN_NAME, TWEET_CONTENT) VALUES(?, ?, ?);", (tweet_id, tweet_user, tweet_textenc))
		conn.commit()
	conn.close()

#---------------------------------
# This function prints out all the archived tweets in the database
#-------------------------------------
def tweet_print_all():
	conn = sqlite3.connect("twitter_tweets.db")
	cursor = conn.execute("SELECT TWEET_KEY, TWEET_SCREEN_NAME, TWEET_CONTENT from Twitter")
	table = cursor.fetchall()
	# print (tabulate(table)) #pending debugging for pretty print of tables
	for i in range(0,len(table)):
		print(table[i])
	conn.close()

#------------------------------
# This function confirms the authentication of the access tokens
#------------------------------
def authenticate_token():
	url_authenticate = "https://api.twitter.com/1.1/account/verify_credentials.json"
	auth_status = requests.get(url_authenticate, auth=auth)
	print ("The HTTP response code for the authorisation check is:",auth_status.status_code)

#---------------------------
# this function deletes archived tweets matching a user name
#---------------------------
def remove_tweets(user_name):
	conn = sqlite3.connect("twitter_tweets.db")
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Twitter WHERE TWEET_SCREEN_NAME=:who", {"who": user_name})
	conn.commit()
	conn.close()

#---------------------------
# this function will return the tweets saved from a particular user
#---------------------------
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

#-------------------------------
# this function will count the number of words in the tweet
#-------------------------------
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

#----------------------------------
# this function will clean up the tweets to remove punctuation and replace with whitespace
#-----------------------------------
def removeNonAlphaNum(text_of_tweets_normalised):
	import re
	return re.sub("[, ( ) ]", " ", text_of_tweets_normalised)

#--------------------------------
# This function removes the stop words using a list stored in separate file
#--------------------------------
def remove_stop_words(tweet_words, stopwords):
	individual_words = tweet_words.split()
	return [w for w in individual_words if not (w in stopwords)]
#---------------------
# The User interface is initialised
#----------------------

interface()

#----------------------
# This section holds miscellaneous comments
# That help with keeping some code handy
#------------------------
# print(json.dumps(tweet_json, sort_keys=True,
		# indent = 4, separators=(",",":"))) #this prints the formatted JSON response from Twitter API
