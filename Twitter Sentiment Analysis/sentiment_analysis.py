import json
from access_credentials import Alchemycredentials
from watson_developer_cloud import AlchemyLanguageV1
from tabulate import tabulate

alchemy_language = AlchemyLanguageV1(api_key = Alchemycredentials["apikey"])
def emotion_check(text):
	return (json.dumps(
	alchemy_language.emotion(text = text
		),
	indent = 2))

def tweet_sentiment(text):
	return (json.dumps(
		alchemy_language.sentiment(
			text = text),
		indent = 2))




