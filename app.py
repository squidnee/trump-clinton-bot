#!flask/bin/python
from flask import Flask
from flask import render_template, request
app = Flask(__name__)

from bot import *
import sys, os
from controllers.data_controller import *

data = get_data()
frames = get_dataframes(data)
df = merge_dataframes(frames)

@app.route("/")
def index():
	template = 'index.html'
	return render_template(template)

@app.route("/prediction", methods=['POST'])
def prediction():
	template = 'prediction.html'
	html = open("./templates/prediction.html").read()
	query = request.form.get('query')
	prediction = bot(query, df)
	return render_template(template, query=query, prediction_story=prediction)

@app.route("/stats/")
def stats():
	pass

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)