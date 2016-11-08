import requests
import bc_11_access_credentials
import json
from requests_oauthlib import OAuth1
import sqlite3


conn = sqlite3.connect("twitter_tweets.db")
conn.execute('''CREATE TABLE IF NOT EXISTS Twitter
		(TWEET_KEY text NOT NULL,
			TWEET_SCREEN_NAME text NOT NULL,
			TWEET_CONTENT text NOT NULL);''')
conn.close()

url_authenticate = "https://api.twitter.com/1.1/account/verify_credentials.json"
auth = OAuth1(bc_11_access_credentials.credentials["consumer_key"], bc_11_access_credentials.credentials["consumer_secret"],
				bc_11_access_credentials.credentials["access_token"], bc_11_access_credentials.credentials["access_token_secret"])
auth_status = requests.get(url_authenticate, auth=auth)
print ("The HTTP response code for the authorisation check is:",auth_status.status_code)

user_name = input("Please provide me with a twitter handle without the @ e.g oti_ian instead of @oti_ian")
tweet_number = input("Please give the number of most recent tweets you want to receive")
url_tweets = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+user_name+"&count="+tweet_number+""
tweet = requests.get(url_tweets, auth=auth)
tweet_json = tweet.json()
# print(json.dumps(tweet_json, sort_keys=True,
		# indent = 4, separators=(",",":"))) #this prints the formatted JSON response from Twitter API
total_tweet = []
total_user = []
total_id = []
conn = sqlite3.connect("twitter_tweets.db")
for i in range(0,len(tweet_json)):
	tweet_user = tweet_json[i]["user"]["screen_name"]
	total_user.append(tweet_user)

	tweet_id = tweet_json[i]["id_str"]
	total_id.append(tweet_id)

	tweet_text = tweet_json[i]["text"]
	tweet_textenc = tweet_text.encode("utf-8", "ignore") #this encodes the text as utf-8 as is received from Twitter
	total_tweet.append(tweet_text)
	conn.execute("INSERT INTO Twitter VALUES(?, ?, ?);", (tweet_id, tweet_user, tweet_textenc))
	conn.commit()

cursor = conn.execute("SELECT TWEET_KEY, TWEET_SCREEN_NAME, TWEET_CONTENT from Twitter")
for row in cursor:
	print("tweet_ID = ", row[0])
	print("tweet_UserName = ", row[1])
	print("tweet_Text = ", row[2], "\n")
conn.close



all_tweet_text = " ".join(total_tweet)
print (all_tweet_text)
print (total_id)
print (total_user)
#-----------------------------
#this section deals with the database
#-------------------------------
