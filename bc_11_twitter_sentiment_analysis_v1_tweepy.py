import tweepy

consumer_key = "LMHP2mSVzCYIijk1O0I0vmkD1"
consumer_secret = "Mn3YFC9Wgf5V4jxPoxp54nmKdE5coXelVDNZ0vuybe12FtlV9f"
access_token = "582659507-aJj2MnmO3mRaCXY5uvf7YS1uIRK7pUNskT3PO8Ut"
access_token_secret = "RehVuyahciuo03z9nC9iOmoyYxWteV31772b74WqrZX9M"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
user_tweets = api.user_timeline(screen_name = "oti_ian", count = 1)

for tweet_user in user_tweets:
	print(tweet_user.text)

for tweet in public_tweets:
	print (tweet.text)
