import json
from access_credentials import Alchemycredentials
from watson_developer_cloud import AlchemyLanguageV1
import datetime
from tabulate import tabulate
#import bc_11_twitter_sentiment_analysis_v1

current_time = datetime.datetime.now()


example_text = "There was once a boy who hardly had any toys or money. Nevertheless, he was a very happy little boy. He said that what made him happy was doing things for others, and that doing so gave him a nice feeling inside. However, no one really believed him; they thought he was loopy"



alchemy_language = AlchemyLanguageV1(api_key = Alchemycredentials["apikey"])
def emotion_check(text):
	return (json.dumps(
	alchemy_language.emotion(text = text
		),
	indent = 2))

# s_print = json.loads(s)
# s_emotion = s_print["docEmotions"]

# aux = [(key, s_emotion[key]) for key in s_emotion]
# aux.sort()
# aux.reverse()
# print(aux)
# # aux = [(tweet_word_list_count[key], key) for key in tweet_word_list_count]
# # aux.sort()
# # aux.reverse()
# return(tabulate(aux, headers=["emotion","probability of emotion"], tablefmt = "fancy_grid"))



