import datetime
import json
import requests
import telebot

LOKLAK_API_URL = "http://loklak.org/api/search.json?q={query}"

bot = telebot.TeleBot("162563966:AAHRx_KauVWfNrS9ADn099kjxqGNB_jqzgo")


def get_tweet_rating(tweet):
    """
    Function that count tweet rating based on favourites and retweets
    """
    return (tweet['retweet_count'] * 2) + tweet['favourites_count']


@bot.message_handler()
def description(message):
    pass


@bot.message_handler(func=lambda m: True)
def search(message):
    result = requests.get(LOKLAK_API_URL.format(query=message.text))
    tweets = json.loads(result.text)['statuses']
    if tweets:
        # Find the best tweet for this search query,
        # by using sorting
        tweets.sort(key=get_tweet_rating, reverse=True)
        tweet = '"{message}" - {author} \n\n{link}'.format(
            message=tweets[0]['text'],
            author=tweets[0]['screen_name'],
            link=tweets[0]['link']
        )
        bot.reply_to(message, tweet)
    else:
        bot.reply_to(message, 'Not found')


@bot.message_handler()
    def description(message):
        pass')

bot.polling()

# Do not stop main thread
while True:
    pass
