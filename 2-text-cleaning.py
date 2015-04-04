#!/usr/bin/python
# -*-coding:UTF-8 -*-

# Download the NLTK resource
from DictMySQLdb import DictMySQLdb
from gensim import corpora, models, similarities
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import pandas as pd
import pickle


# Get the production title from database
# nltk.download()

# Database connection
pd_db = DictMySQLdb(user='root', passwd='', host='127.0.0.1', db='product')

# Download from db
product = pd_db.select(tablename='item', field=['title', 'root_category_id'])
# Convert to pandas DataFrame
product = pd.DataFrame([{'title': i[0], 'cat': i[1]} for i in product])

# Get root categories
category = pd_db.select(tablename='category', field=['id', 'name'], value={'upper_level': 1})
category = pd.DataFrame([{'cat': i[0], 'cat_name': i[1]} for i in category])

product_category = product.merge(category, on='cat', how='left')

# Remove stopwords and stemming
stopwords = nltk.corpus.stopwords.words("english")
porter_stemmer = PorterStemmer()
tokenizer = RegexpTokenizer(r'\w+')
product['cleaned_title'] = product['title'].map(lambda row: tokenizer.tokenize(' '.join([porter_stemmer.stem(word.lower()) for word in row.split() if word not in stopwords])))

# Build dictionary
dictionary = corpora.Dictionary(product['cleaned_title'])

# Translate the documents into vectors based on the dictionary
corpus = [dictionary.doc2bow(text) for text in product['cleaned_title']]

# Build TF-IDF model
tfidf = models.TfidfModel(corpus)

# Calculate the TF-IDF value of the documents
corpus_tfidf = tfidf[corpus]

# Build LSI model for dimentional reduction
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100)
lsi.print_topics(100)

# Get the text features of original documents
corpus_lsi = lsi[corpus_tfidf]

# Build the index of the similarity
index = similarities.MatrixSimilarity(lsi[corpus])

# Save the LSI model and the similarity matrix
pickle.dump(lsi, open("lsi.obj", "w"))
pickle.dump(index, open("ind.obj", "w"))
pickle.dump(dictionary, open("dictionary.obj", "w"))
pickle.dump(product_category['cat_name'], open("cat_list.obj", "w"))

# Input the new text
query = "iPhone 6 Plus"

# Run the same text processing for the input text
query_bow = dictionary.doc2bow(tokenizer.tokenize(' '.join([porter_stemmer.stem(word.lower()) for word in query.split() if word not in stopwords])))

# Translate the text into the space we build with LSI model
query_lsi = lsi[query_bow]

# Calculate the text simimarity amoung all the documents
sims = index[query_lsi]

# Sort the result
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
print sort_sims[0:5]