from stop_words import get_stop_words
stopwords = get_stop_words("english")
# print (stopword_generator)
stopwords += [".", ",", "?", "*", "/"]