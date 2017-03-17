# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import csv
import json
import requests
import os
import re
import pandas as pd
from os.path import exists, join

DATA_SRC = 'static'

if not exists(DATA_SRC):
	os.mkdir(DATA_SRC)

TWEET_PATH = 'https://raw.githubusercontent.com/WiMLDS/election-data-hackathon/master/clinton-trump-tweets/data/tweets.csv'
#TODO: Decide whether or not you want to download this
TWEET_FILE = 'tweets.json'

def return_tweet_file():
	return TWEET_PATH

def make_dataframe(file):
	# TODO: Decide whether or not to parse / remove hashtags
	df = pd.read_csv(file, index_col=0, encoding='utf-8')
	# Removes retweets
	df = df[['handle', 'text', 'is_retweet','source_url']]
	df = df.loc[df['is_retweet'] == False]
	df = df.copy().reset_index(drop=True)

	android = ['android']
	
	df['label'] = df['handle'].apply(lambda x: get_candidate_label(x))
	df['text'] = df['text'].apply(lambda x: x.lower().split('http')[0])
	df['text'] = df['text'].apply(lambda x: remove_mentions(x))
	df[~df['source_url'].str.contains('|'.join(android))]

	new_df = df[['label','text']]
	return new_df

def get_candidate_label(handle):
	if 'HillaryClinton' in str(handle):
		return 'Clinton'
	else: return 'Trump'

def remove_mentions(text):
	return re.sub('(\@[A-Za-z_]+)', '', text)

def make_csv_file(df):
	df.to_csv(join(DATA_SRC,TWEET_FILE))

def grab_tweet_dataframe():
	file = return_tweet_file()
	df = make_dataframe(file)
	return df

if __name__ == '__main__':
	df = grab_tweet_dataframe()
	print(df)