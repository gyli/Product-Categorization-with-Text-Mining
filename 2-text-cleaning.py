#!/usr/bin/python
# -*-coding:UTF-8 -*-

# Download the NLTK resource
from DictMySQLdb import DictMySQLdb
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import pandas as pd


# Get the production title from database
nltk.download()

# Database connection
pd_db = DictMySQLdb(user='root', passwd='', host='127.0.0.1', db='product')

# Download from db
product = pd_db.select(tablename='item', field=['title', 'root_category_id'])
# Convert to pandas DataFrame
product = pd.DataFrame([{'title': i[0], 'cat': i[1]} for i in product])

# Remove stopwords and stemming
stopwords = nltk.corpus.stopwords.words("english")
porter_stemmer = PorterStemmer()
tokenizer = RegexpTokenizer(r'\w+')
product['cleaned_title'] = product['title'].map(lambda row: tokenizer.tokenize(' '.join([porter_stemmer.stem(word.lower()) for word in row.split() if word not in stopwords])))
