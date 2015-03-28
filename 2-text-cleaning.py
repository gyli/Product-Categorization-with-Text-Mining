#!/usr/bin/python
# -*-coding:UTF-8 -*-

# Download the NLTK resource
import nltk
nltk.download()

# Get the production title from database
import DictMySQLdb


# Stopwords removing
from nltk.corpus import stopwords
cachedStopWords = stopwords.words("english")


text = 'hello bye the the hi'
text = ' '.join([word for word in text.split() if word not in cachedStopWords])


from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()
porter_stemmer.stem('beautiful')