import sys
import json, csv
import pandas as pd
from os.path import join

from libraries import debate_lib, speech_lib, tweet_lib

def get_data_src():
	return './static'

def load_data():
	speech_lib.fetch_clinton_speeches()
	speech_lib.fetch_trump_speeches()
	debate_lib.get_debates()

def get_data(preloaded=False):
	'''First load the data'''
	if not preloaded: load_data()
	data = {}
	'''Get debate data'''
	data['trump_debate_file'] = debate_lib.trump_debate_file()
	data['clinton_debate_file'] = debate_lib.clinton_debate_file()
	'''Get speech data'''
	data['trump_speech_file'] = speech_lib.trump_speech_file()
	data['clinton_speech_file'] = speech_lib.trump_speech_file()
	'''Get tweet data'''
	data['tweet_data'] = tweet_lib.return_tweet_file()
	return data

def get_dataframes(data):
	dataframe = {}
	data_src = get_data_src()
	'''Get debate dataframes'''
	dataframe['trump_debates'] = pd.read_json(join(data_src, data['trump_debate_file']))
	dataframe['clinton_debates'] = pd.read_json(join(data_src, data['clinton_debate_file']))
	'''Get speech dataframes'''
	dataframe['trump_speeches'] = pd.read_json(join(data_src, data['trump_speech_file']))
	dataframe['clinton_speeches'] = pd.read_json(join(data_src, data['clinton_speech_file']))
	'''Get tweet dataframes'''
	dataframe['tweets'] = tweet_lib.grab_tweet_dataframe()
	return dataframe

def merge_dataframes(df):
	df_deb = pd.concat([df['trump_debates'], df['clinton_debates']])
	df_sp = pd.concat([df['trump_speeches'], df['clinton_speeches']])
	merged_df = pd.concat([df_deb, df_sp])
	merged_df = pd.concat([merged_df, df['tweets']])
	return merged_df