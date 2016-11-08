import requests
import bc_11_access_credentials
import json
from requests_oauthlib import OAuth1

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
for i in range(0,len(tweet_json)):
	tweet_text = tweet_json[i]["text"]
	total_tweet.append(tweet_text)

all_tweet_text = " ".join(total_tweet)
print (all_tweet_text)