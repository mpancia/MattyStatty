from flask import Flask
from flask import render_template, session, url_for, request, redirect
import pandas as pd 
import collections
import os
import string 
from os import environ 
import tweepy
import json 
app = Flask(__name__)
app.config.update(
	DEBUG = True,
)

@classmethod
def parse(cls, api, raw):
	status = cls.first_parse(api, raw)
	setattr(status, 'json', json.dumps(raw))
	return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse

def letter_freq(tweetStream, handle = "matty_books"):
	data = tweetStream.user_timeline(screen_name = handle, count = 100)
	tweetString = str()
	for tweet in data:
		tweetString = tweetString + tweet.text.lower() + " "
	counter = collections.Counter(tweetString)
	n = sum(counter.values())
	return {char.encode('ascii', 'ignore') : float(count) / n for char, count in counter.most_common() if char in string.lowercase}

def freq_to_df(freq):
	return pd.DataFrame(freq.items(), columns = ['letter', 'frequency'])

def word_freq(tweetStream, handle="matty_books"):
	badwords = ['a', 'the', 'of', 'rt', 'if', 'to', 'for', 'on', 'is', '/', '-', 'a', 'this', 'and']
	data = tweetStream.user_timeline(screen_name=handle,count=200)
	tweetString = str()
	for tweet in data:
		tweetString = tweetString + tweet.text.lower() + " "
	tweetString = tweetString.split()
	for word in tweetString:
		if word in badwords or word[0] == '@':
			tweetString.remove(word)
	counter = collections.Counter(tweetString)
	n = sum(counter.values())
	return {char.encode('ascii', 'ignore') : float(count)  for char, count in counter.most_common(20)}
	


app.secret_key = environ.get('global_secret')

@app.route('/',methods=('GET', 'POST'))
@app.route('/index',methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		session['handle'] = request.form.get("handle")
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
	freq = freq.sort('frequency', ascending=False)
	freq = freq.to_json(orient='records')
	freq = freq[1:-1]
	return render_template("letter.html", freq=freq)

@app.route('/word')
def word():
	consumer_key = environ.get('c_key')
	consumer_secret = environ.get('c_sec')
	access_token_key = environ.get('a_key')
	access_token_secret = environ.get('a_sec')
	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, secure=True)
	freq = word_freq(api, session['handle'])
	freq = pd.DataFrame(freq.items(), columns = ['word', 'frequency'])
	freq = freq.sort('frequency', ascending=False)
	freq = freq.to_json(orient='records')
	return render_template("word.html", freq=freq)

@app.route('/info')
def info():
	consumer_key = environ.get('c_key')
	consumer_secret = environ.get('c_sec')
	access_token_key = environ.get('a_key')
	access_token_secret = environ.get('a_sec')
	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, secure=True)
	jtweets = api.get_user(session['handle'])._json 
	return render_template("info.html", jtweets = jtweets)

@app.route('/tweets')
def tweetpage():
	consumer_key = environ.get('c_key')
	consumer_secret = environ.get('c_sec')
	access_token_key = environ.get('a_key')
	access_token_secret = environ.get('a_sec')
	auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_token_key, access_token_secret)
	api = tweepy.API(auth, secure=True)
	total =api.get_user(session['handle']).statuses_count
	tweetlist = list()
	timeline = api.user_timeline(screen_name = session['handle'], count = 200)
	for i in timeline:
		tweetlist.append(i)
	total = total - 200
	tweetlist.sort(key=lambda r : r.created_at, reverse=False)
	latest_id = tweetlist[0].id - 1 
	while total > 0:
		timeline = api.user_timeline(screen_name = session['handle'], count = 200, max_id=(latest_id))
		for i in timeline:
			tweetlist.append(i)
		total = total - 200
		tweetlist.sort(key=lambda r : r.created_at, reverse=False)
		latest_id = tweetlist[0].id - 1 
	tweetlist.sort(key=lambda r : r.created_at, reverse=True)	
	tweets = [{ 'text' : tweet.text} for tweet in tweetlist]
	return render_template("tweets.html",tweets=tweets)	

@app.before_request
def set_client_session():
	if 'handle' not in session:
		session['handle'] = None

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, debug = True)