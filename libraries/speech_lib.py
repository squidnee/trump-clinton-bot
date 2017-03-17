# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from os.path import exists, join

DATA_SRC = 'static'
CLINTON_SPEECH_PATH = 'http://www.presidency.ucsb.edu/2016_election_speeches.php?candidate=70&campaign=2016CLINTON&doctype=5000'
TRUMP_SPEECH_PATH = 'http://www.presidency.ucsb.edu/2016_election_speeches.php?candidate=45&campaign=2016TRUMP&doctype=5000'

CLINTON_SPEECH_FILE = 'clinton_speeches.json'
TRUMP_SPEECH_FILE = 'trump_speeches.json'

if not exists(DATA_SRC):
	os.mkdir(DATA_SRC)

def trump_speech_file():
	return TRUMP_SPEECH_FILE

def clinton_speech_file():
	return CLINTON_SPEECH_FILE

def fetch_candidate_speeches(candidate_path, candidate_file, label):
	''' Fetches candidate speeches from the Internet.'''
	resp = requests.get(candidate_path)
	soup = BeautifulSoup(resp.text, 'lxml')
	elems = soup.select('td.listdate a')
	hrefs = []
	base = 'http://www.presidency.ucsb.edu/'
	for elem in elems:
		hrefs.append(elem.attrs['href'][3:])

	speeches = []
	for href in hrefs:
		url = base + href
		speeches.append(candidate_speech_helper(url))

	df = make_dataframe(speeches, label, base)

	data_path = join(DATA_SRC, candidate_file)

	write_df_to_json(data_path, df)

def candidate_speech_helper(url):
	resp = requests.get(url)
	soup = BeautifulSoup(resp.text, 'lxml')
	return soup.select('span.displaytext')[0].text

def make_dataframe(speeches, label, base=None):
	frame = dict()
	labels = [label] * len(speeches)
	speech = pd.Series(speeches)
	label = pd.Series(labels)
	frame['label'] = label
	frame['text'] = speech
	return pd.DataFrame(frame)

def write_df_to_json(path, df):
	df.to_json(path)
	print('New file at {path} created.'.format(path=path))

def fetch_clinton_speeches(speech_path=CLINTON_SPEECH_PATH, speech_file=CLINTON_SPEECH_FILE):
	if not exists(join(DATA_SRC, speech_file)):
		print('Building Clinton speech data...')
		fetch_candidate_speeches(speech_path, speech_file, label='Clinton')
	else: print("File {path} already exists.".format(path=speech_file))

def fetch_trump_speeches(speech_path=TRUMP_SPEECH_PATH, speech_file=TRUMP_SPEECH_FILE):
	if not exists(join(DATA_SRC, speech_file)):
		print('Building Trump speech data...')
		fetch_candidate_speeches(speech_path, speech_file, label='Trump')
	else: print("File {path} already exists.".format(path=speech_file))

if __name__ == '__main__':
	print('Building data from speech paths...')
	fetch_clinton_speeches()
	fetch_trump_speeches()