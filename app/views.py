from app import app
from flask import render_template, session, url_for, request, redirect
from twython import Twython	
import pandas as pd 
import collections
from os import environ
def letter_freq(tweetStream, handle = "matty_books"):
    user_timeline = tweetStream.get_user_timeline(screen_name=handle)
    tweetString = str()
    for tweet in user_timeline:
        tweetString = tweetString + tweet['text'].lower() + " "
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
	twitter = Twython(environ.get('APP_KEY'), environ.get('APP_SECRET'), environ.get('AUTH_ID'), environ.get('AUTH_SECRET'))
	freq = freq_to_df(letter_freq(twitter,session['handle']))
	freq = freq[freq.letter != ' ']
	freq = freq[freq.letter != '' ]
	freq = freq[freq.letter != '"' ]
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
