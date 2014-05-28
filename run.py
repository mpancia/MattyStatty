from flask import Flask
from flask import render_template, session, url_for, request, redirect
import pandas as pd 
import collections
import os
from os import environ 
import tweepy
import json 
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)
def letter_freq(tweetStream, handle = "matty_books"):
	data = tweetStream.user_timeline(handle, count=100)
	tweetString = str()
	for tweet in data:
		tweetString = tweetString + tweet.text.lower() + " "
		counter = collections.Counter(tweetString)
		n = sum(counter.values())
		return {char.encode('ascii', 'ignore') : float(count) / n for char, count in counter.most_common() if char != ' ' and char != '@'}

def freq_to_df(freq):
    return pd.DataFrame(freq.items(), columns = ['letter', 'frequency'])

app.secret_key = 'why would I tell you my secret key?'

@app.route('/',methods=('GET', 'POST'))
@app.route('/index',methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		session['handle'] = request.form.get("handle", None)
	return render_template("index.html")

@app.route('/handle')
def login():
	return render_template("login.html")

@app.route('/letter')
def letter():
    consumer_key = environ.get('c_key')
    consumer_secret = environ.get('c_sec')
    access_token_key = environ.get('a_key')
    access_token_secret = environ.get('a_sec')
	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, secure=True)
	freq = freq_to_df(letter_freq(api,session['handle']))
	freq = freq.ix[freq.letter != ' ']
	freq = freq.ix[freq.letter != '' ]
	freq = freq.ix[freq.letter != '"' ]
	freq = freq.sort('letter')
	freq = freq.to_json(orient='records')
	freq = freq[1:-1]
	return render_template("letter.html", freq=freq)

@app.route('/word')
def word():
	return render_template("word.html")

@app.route('/force')
def force():
	return render_template("force.html")

@app.before_request
def set_client_session():
	if 'handle' not in session:
		session['handle'] = None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)