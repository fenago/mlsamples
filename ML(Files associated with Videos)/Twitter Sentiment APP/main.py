from flask import Flask, render_template, request
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import re
from flask_ngrok import run_with_ngrok

def authenticate():
    consumer_key = "GCeaLvXMf0vhyFWxOmfveIaw1"
    consumer_secret = "blWTrbFx5V1yv3swilaQDI5vvdUJNH66QyeoXO4vFMu3vQqy8S"

    access_token = "840489927284514817-5JaikUdITcdmAcc5klw77FpIWKfUFIZ"
    access_secret = "mqrRablqauzEhuiQK82ZwqxjxKQK7P8kfd09Ju2zHxouI"

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    return api


app = Flask(__name__, static_url_path="/static")
api = authenticate()
run_with_ngrok(app)

def clean_text(tweet):
  return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())

def save_fig(results):
    pos,neg,neut = [0,0,0]
    for tweet in results:
        polarity = TextBlob(clean_text(tweet.text)).sentiment.polarity 
        if polarity > 0:
            pos += 1
        elif polarity < 0:
            neg += 1
        else:
            neut += 1
    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [pos, neg, neut]  
    plt.clf()
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes,  explode = (0, 0.1, 0), labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  
    plt.savefig("static/images/imageToDisplay.jpg")

@app.route('/', methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        textToSearch = request.form.get("topic")
        howMany = request.form.get("number")
        results = api.search(q = textToSearch, count = howMany)
        save_fig(results)
        return render_template("diplay.html")
    return render_template("index.html")

if __name__ == "__main__":
    app.run()