# coding: utf-8

''' This is the bot that does most of the behind-the-scenes data processing.'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from libraries.speech_lib import *
from libraries.debate_lib import *
from libraries.tweet_lib import *

from sys import argv

import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
import flask
import json

from os.path import exists, join, dirname, abspath

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

DATA_SRC = 'static'

nltk.download('punkt')

if not exists(DATA_SRC):
	os.mkdir(DATA_SRC)

def split_words(text):
	# Splits words into tokens.
	# TODO: tokenize by lemmas (such that 'policies' is given same weight as 'policy', for example)
	# Unfortunately, can't seem to do this in a way that doesn't utilize NLTK (and NLTK
	# permissions are messed up on my own computer)
	tokens = word_tokenize(text.lower())
	return tokens

def pull_more_statistics(df):
	# converts the collection of text snippets to a matrix of token counts (using split_words)
	# note: bow refers to 'bag of words'
	bow_transformer = CountVectorizer(analyzer=split_words).fit(df['text'])
	bow_text = bow_transformer.transform(df['text'])

	# returns the shape and sparsity of the matrix
	print('Shape of the sparse matrix:', bow_text.shape)
	print('Matrix sparsity: %.2f%%' % (100.0 * bow_text.nnz / (bow_text.shape[0] * bow_text.shape[1])))

	# normalizes the term matrix (i.e. scales down the matrix so that the least frequent words
	# count less than more frequent words)
	tfidf_transformer = TfidfTransformer().fit(bow_text)
	tfidf_text = tfidf_transformer.transform(bow_text)
	print(tfidf_text.shape)

	# reports the accuracy on the training set
	nbayes = MultinomialNB().fit(tfidf_text, df['label'])
	preds = nbayes.predict(tfidf_text)
	tr_acc = accuracy_score(df['label'], preds)
	print("Accuracy on training set:  %.2f%%" % (100 * tr_acc))

	# provides a classification report (precision, recall, f1-scores), which essentially
	# is a more in-depth report on the accuracy of the model
	print(classification_report(df['label'], preds))

	grab_highest_probability_terms_per_candidate(bow_transformer, nb, max_feature_length=4)

def run_data_through_pipeline(df):
	# splits the sets into train and test sets
	train, test, label_train, label_test = split_sets(df)

	# builds the pipeline for
	pipeline = Pipeline([
    ('bow', CountVectorizer(analyzer=split_words)),
    ('tfidf', TfidfTransformer()),
    ('classifier', MultinomialNB()),
    ])

	scores = cross_val_score(pipeline, train, label_train, cv=10, scoring='accuracy', n_jobs=-1)
	print(scores)

	# the params (parameters) are essentially different options that the model can choose
	# it'll choose the parameter set that results in the best-performing model
	params = {'tfidf__use_idf': (True, False) } # TODO: Add more of these!

	grid = GridSearchCV(pipeline, params, refit=True, scoring='accuracy')
	grid_train = grid.fit(train, label_train)
	test_preds = grid_train.predict(test)
	#print(classification_report(label_test, test_preds))
	#print("Accuracy on test set:  %.2f%%" % (100 * (grid_train.grid_scores_[0][1])))

	bow_transformer = CountVectorizer(analyzer=split_words).fit(df['text'])

	return grid_train

def grab_highest_probability_terms_per_candidate(bow_transformer, nb, max_feature_length=4):
	top_clinton = {}; top_trump = {}
	features = bow_transformer.get_feature_names()
	for feature in features:
		prob = nb.predict_proba([feature])[0][0]
		if len(feature) >= max_feature_length:
			if prob > 0.5: top_clinton[feature] = prob
			elif prob < 0.5: top_trump[feature] = prob

	top10_trump = sorted(top_trump, key=top_trump.get, reverse=False)[:10]
	top10_clinton = sorted(top_clinton, key=top_clinton.get, reverse=True)[:10]
	
	print(top10_trump, top10_clinton)

def split_sets(df):
	text_train, text_test, label_train, label_test = \
    train_test_split(df['text'], df['label'], test_size=0.2, random_state=1)
	#print(len(text_train), len(text_test), len(text_train) + len(text_test))
	return (text_train, text_test, label_train, label_test)

def predict(nb, query):
	probability = round(max(nb.predict_proba([query])[0]) * 100, 1)
	label = nb.predict([query])[0]
	off_probability = 100 - probability
	off_label = 'Clinton' if 'Trump' in label else 'Trump'
	prediction = '''Based on my calculations, this is {prob}% likely to be said by {label} and
	{off_prob}% likely to be said by {off_label}'''.format(prob=probability,\
				label=label, off_prob=off_probability, off_label=off_label)
	return prediction

def menu():
	return '''If you're interested in seeing more statistics about this data set, type 'S'!'''

def bot(query, df, more_stats=False):
	df.text.apply(split_words)

	if more_stats:
		pull_more_statistics(df)
	else:
		naive_bayes = run_data_through_pipeline(df)
		prediction = predict(naive_bayes, query)
		print(prediction)
		print(menu)
	return prediction

if __name__ == '__main__':
	more_stats = False
	if len(argv) == 2 and argv[1].upper() == 'S':
			more_stats = True
	elif len(argv) < 2:
		print("Please enter some text!")
	else:
		query = argv[1]
		bot(query.lower(), more_stats)