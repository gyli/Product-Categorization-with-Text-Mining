#!/usr/bin/python
# -*-coding:UTF-8 -*-

from gensim import corpora, models, similarities



dictionary = corpora.Dictionary(product['title'])

corpus = [dictionary.doc2bow(text) for text in product['title']]

tfidf = models.TfidfModel(corpus)

corpus_tfidf = tfidf[corpus]


lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100)
lsi.print_topics(100)

corpus_lsi = lsi[corpus_tfidf]

index = similarities.MatrixSimilarity(lsi[corpus])



query = "iPhone 6 Plus"
query_bow = dictionary.doc2bow(tokenizer.tokenize(' '.join([porter_stemmer.stem(word.lower()) for word in query.split() if word not in stopwords])))
query_lsi = lsi[query_bow]
sims = index[query_lsi]
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
sort_sims[0:5]

product.iloc[25535]