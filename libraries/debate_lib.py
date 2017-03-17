# coding: utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import re
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from os.path import exists, join

DATA_SRC = 'static'
DEBATES_PATH = 'http://www.presidency.ucsb.edu/debates.php'

CLINTON_DEBATE_FILE = 'clinton_debates.json'
TRUMP_DEBATE_FILE = 'trump_debates.json'

if not exists(DATA_SRC):
	os.mkdir(DATA_SRC)

def trump_debate_file():
	return TRUMP_DEBATE_FILE

def clinton_debate_file():
	return CLINTON_DEBATE_FILE

def parse_by_candidate_name(hrefs):
	'''We are assuming here that the candidates are Clinton and Trump.'''
	clinton_text = []; trump_text = []
	for url in hrefs:
		resp = requests.get(url)
		soup = BeautifulSoup(resp.text, 'lxml')
		speech = soup.select('span.displaytext')[0].text
		data = re.split('([A-Z]+:)', speech)
		for index, frag in enumerate(data):
			if 'TRUMP:' in frag:
				trump_text.append(data[index+1])
			elif 'CLINTON:' in frag:
				clinton_text.append(data[index+1])
		return clinton_text, trump_text

def sort_by_recent_election(elems):
	latest_index = 0
	for (date, title) in elems:
		year = date.split()
		if len(year) is 0: continue
		elif str(year[2]) == '2015' or str(year[2]) == '2016': latest_index += 1
	return latest_index

def save_data(text, path, label):
	frame = dict()
	debate_text = pd.Series(text)
	labels = [label] * len(text)
	frame['label'] = label
	frame['text'] = debate_text
	df = pd.DataFrame(frame)

	data_path = join(DATA_SRC, path)
	if not exists(data_path):
		df.to_json(data_path)
		out = 'New file at {path} created.'.format(path=data_path)
	else: out = "File {path} already exists.".format(path=data_path)
	print(out)

def get_debates():
	resp = requests.get(DEBATES_PATH)
	soup = BeautifulSoup(resp.text, 'lxml')
	dates = soup.select('td.docdate')
	dates = [d.text for d in dates]
	titles = soup.select('td.doctext a')
	elems = zip(dates, titles)
	cutoff = sort_by_recent_election(elems)
	recent_debates = elems[:cutoff+1]
	hrefs = []
	for debate in recent_debates:
		hrefs.append(debate[1].attrs['href'])

	clinton_text, trump_text = parse_by_candidate_name(hrefs)

	if not exists(join(DATA_SRC, CLINTON_DEBATE_FILE)):
		print("Building Clinton debate data...")
		save_data(clinton_text, CLINTON_DEBATE_FILE, label='Clinton')
	else: print("File {path} already exists.".format(path=join(DATA_SRC,CLINTON_DEBATE_FILE)))

	if not exists(join(DATA_SRC, TRUMP_DEBATE_FILE)):
		print("Building Trump debate data...")
		save_data(trump_text, TRUMP_DEBATE_FILE, label='Trump')
	else: print("File {path} already exists.".format(path=join(DATA_SRC,TRUMP_DEBATE_FILE)))

if __name__ == '__main__':
	print("Building data from the debates...")
	get_debates()