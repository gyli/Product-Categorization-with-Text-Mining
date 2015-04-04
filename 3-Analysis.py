#!/usr/bin/python
# -*-coding:UTF-8 -*-

from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
import pickle
import sys


lsi = pickle.load(open("lsi.obj", "r"))
index = pickle.load(open("ind.obj", "r"))
dictionary = pickle.load(open("dictionary.obj", "r"))
cat_list = pickle.load(open("cat_list.obj", "r"))

# Input the new text
query = "Apple MacBook Air MJVE2LL/A 13.3-Inch Laptop (128 GB) NEWEST VERSION"
query = sys.argv[1]

tokenizer = RegexpTokenizer(r'\w+')
porter_stemmer = PorterStemmer()
stopwords = [u'i',
             u'me',
             u'my',
             u'myself',
             u'we',
             u'our',
             u'ours',
             u'ourselves',
             u'you',
             u'your',
             u'yours',
             u'yourself',
             u'yourselves',
             u'he',
             u'him',
             u'his',
             u'himself',
             u'she',
             u'her',
             u'hers',
             u'herself',
             u'it',
             u'its',
             u'itself',
             u'they',
             u'them',
             u'their',
             u'theirs',
             u'themselves',
             u'what',
             u'which',
             u'who',
             u'whom',
             u'this',
             u'that',
             u'these',
             u'those',
             u'am',
             u'is',
             u'are',
             u'was',
             u'were',
             u'be',
             u'been',
             u'being',
             u'have',
             u'has',
             u'had',
             u'having',
             u'do',
             u'does',
             u'did',
             u'doing',
             u'a',
             u'an',
             u'the',
             u'and',
             u'but',
             u'if',
             u'or',
             u'because',
             u'as',
             u'until',
             u'while',
             u'of',
             u'at',
             u'by',
             u'for',
             u'with',
             u'about',
             u'against',
             u'between',
             u'into',
             u'through',
             u'during',
             u'before',
             u'after',
             u'above',
             u'below',
             u'to',
             u'from',
             u'up',
             u'down',
             u'in',
             u'out',
             u'on',
             u'off',
             u'over',
             u'under',
             u'again',
             u'further',
             u'then',
             u'once',
             u'here',
             u'there',
             u'when',
             u'where',
             u'why',
             u'how',
             u'all',
             u'any',
             u'both',
             u'each',
             u'few',
             u'more',
             u'most',
             u'other',
             u'some',
             u'such',
             u'no',
             u'nor',
             u'not',
             u'only',
             u'own',
             u'same',
             u'so',
             u'than',
             u'too',
             u'very',
             u's',
             u't',
             u'can',
             u'will',
             u'just',
             u'don',
             u'should',
             u'now']

# Run the same text processing for the input text
query_bow = dictionary.doc2bow(tokenizer.tokenize(
    ' '.join([porter_stemmer.stem(word.lower()) for word in query.split() if word not in stopwords])))

# Translate the text into the space we build with LSI model
query_lsi = lsi[query_bow]

# Calculate the text simimarity amoung all the documents
sims = index[query_lsi]

# Sort the result
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])

print cat_list[[i[0] for i in sort_sims[0:10]]]
print cat_list[[i[0] for i in sort_sims[0:5]]].value_counts().index[0]