# Who (says) it: Trump or Clinton?
An app made for Stanford's COMM 113, winter 2017.

## Background
This is a simple Flask application that takes in a query (e.g. "Make America Great Again!") and predicts whether Trump or Clinton said it
by returning the percent likelihood for each.

## Usage
Download and `cd` into the repo, then run the application using `python app.py`.
Then visit the main page of the application at http://127.0.0.1:5000/. It should be pretty straightforward from there.

You may need to download additional dependencies (e.g. Flask, NLTK, pandas, scipy, sklearn). You can download them by typing `pip install -r requirements.txt`
while you're in the directory.

## Data
I downloaded data from a database of Trump/Clinton speeches and debates in which both were involved. 
I also downloaded both candidates' recent (circa 2016) tweets from [here](https://raw.githubusercontent.com/WiMLDS/election-data-hackathon/master/clinton-trump-tweets/data/tweets.csv).

Downloading the speeches were fairly straightforward. I separated each one into a dataframe using pandas (with features 'label' and 'text') and then wrote the dataframe to a json file.
I did the same for the debate data, but since the debates were all on one page (along with the debates from former elections), I had to limit my search to debates that occurred
no earlier than 2015 (as to avoid instances of 'Clinton' that referred to Bill and not Hillary).
With the Twitter data, I removed all retweets and (in Trump's case) all non-Android tweets, so as to reflect his own statements. All of this data went into a dataframe
which was then written to json.
In hindsight, this was mostly to fulfill the project requirements, but I'm not sure how necessary it is without a database, and it may actually make the program run slower.

As for the machine learning part, I split each word in the dataframe into separate words, then used sklearn to convert the collection of text snippets to a matrix of token counts.
I then normalized the term matrix, such that the least frequent words were weighted less than more frequent words.
Finally, I ran the data through a pipeline, and used a Naive Bayes classifier to calculate the prediction. This model is trained on a training set and a test set on a per-query basis, which makes the loading a lot slower
and is definitely something to fix, but doing so would probably require adding a database, which might be overkill for this particular assignment (but would be worth doing in the future).

## Things to Include
- A database to make the thing run faster (there's a note on this in the landing page)
- Filling in the extra statistics page (e.g. top 10 words used by each candidate)
- (Potentially) just reveal the name of the person that most likely said the term instead of providing scores for both

## Inspiration
I mainly drew inspiration from [this Kaggle competition](https://www.kaggle.com/benhamner/clinton-trump-tweets) and [this blog post](https://benheubl.github.io/machine%20learning/navie-bayes/).
