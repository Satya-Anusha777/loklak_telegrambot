import os
import json
import requests
import telebot

LOKLAK_API_URL = "http://loklak.org/api/search.json?q={query}"

bot = telebot.TeleBot(os.environ['LOKLAK_TELEGRAM_TOKEN'])
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
    answer = '"{message}" - {author} \n\n{link}\n\n{more} more tweets. /next_tweet'.format(
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
    result = requests.get(LOKLAK_API_URL.format(query=message.text))
    try:
        tweets = json.loads(result.text)['statuses']
    except ValueError:
        bot.reply_to(message, 'Not found')
        return
    if tweets:
        # Find the best tweet for this search query,
        # by using sorting
        tweets.sort(key=get_tweet_rating)
        tweet = tweets.pop()
        user_results[message.from_user.id] = tweets
        bot.reply_to(message, tweet_answer(tweet, len(tweets)))
    else:
        # Delete words from message until result is not avaliable
        words = message.text.split()[:-1]
        if words:
            message.text = ' '.join(words)
            search(message)
        else:
            bot.reply_to(message, 'Not found')

bot.polling()

# Do not stop main thread
while True:
    pass
