import os
import json
import requests
import telebot
from telebot import types
LOKLAK_API_URL = "http://loklak.org/api/search.json?q={query}"

bot = telebot.TeleBot("")
user_results = {}



def get_tweet_rating(tweet):
    """
    Function that count tweet rating based on favourites and retweets
    """
    return (tweet['retweet_count'] * 2) + tweet['favourites_count']


def tweet_answer(tweet, tweets_left):
    """
    Function that making text answer from tweet object
    """
    answer = '"{message}" - {author} \n\n{link}\n\n{more} more tweets.'.format(
        message=tweet['text'],
        author=tweet['screen_name'],
        link=tweet['link'],
        more=tweets_left
    )
    return answer


@bot.message_handler(commands=['start', 'help'])
def description(message):
    bot.reply_to(message,
        "loklak.org bot - simple Telegram bot for searching tweets.\n"
        "Just send a message with your query and bot will process it, "
        "using loklag.org API. \n"
        "If you want to contribute, project is open source: "
        "https://github.com/sevazhidkov/tweets-search-bot"
    )
@bot.message_handler(commands=['next-tweet', 'next_tweet'])
def next_tweet(message):
    user_id = message.from_user.id
    if user_id in user_results and user_results[user_id]:
        tweet = user_results[user_id].pop()
        bot.reply_to(message, tweet_answer(tweet, len(user_results[user_id])))
    else:
        bot.reply_to(message, "You haven't searched anything.")


@bot.message_handler(func=lambda m: True)
def search(message):
    query_msg = message.text.lower()
    result = requests.get(LOKLAK_API_URL.format(query=query_msg))
    try:
        tweets = json.loads(result.text)['statuses']
    except ValueError:
        return
    if tweets:
        # Find the best tweet for this search query,
        # by using sorting
        tweets.sort(key=get_tweet_rating)
        tweet = tweets.pop()
        user_results[message.from_user.id] = tweets
        #show a botton on top of input
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup.add('/next-tweet')
        bot.reply_to(message, tweet_answer(tweet, len(tweets)), reply_markup=markup)
    else:
        # Delete words from message until result is not avaliable
        #Strategy: keep removing the smallest word in a sentence
        words = query_msg.split()
        if(len(words) > 1):
            words.sort(key = len)
            del words[0]
            reconstructed = ""
            for word in words:
                reconstructed += word + " "
            message.text = reconstructed
            search(message)
        else:
            bot.reply_to(message, '404 Not found')

bot.polling()
