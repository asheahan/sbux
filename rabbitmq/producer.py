
import json
import pika
import sys
import time
import tweepy

# Load auth configuration from file
with open('./config.json') as config_file:
    TWITTER_CONFIG = json.load(config_file)["twitter"]

AUTH = tweepy.OAuthHandler(TWITTER_CONFIG["consumer_key"], TWITTER_CONFIG["consumer_secret"])
AUTH.set_access_token(TWITTER_CONFIG["access_token"], TWITTER_CONFIG["access_secret"])

api = tweepy.API(AUTH)

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        # Setup RabbitMQ Connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()

        # Set max queue size
        args = {"x-max-length" : 2000}

        # self.channel.queue_declare(queue='twitter_topic_feed', arguments=args)
        # Exchange with fanout to all consumers
        self.channel.exchange_declare(exchange='twitter',
                                      type='fanout')

    def on_status(self, status):
        data = {}
        data['text'] = status.text
        data['created_at'] = time.mktime(status.created_at.timetuple())
        data['geo'] = status.geo
        data['source'] = status.source

        # Queue the tweet
        # self.channel.basic_publish(exchange='',
        #                            routing_key='twitter_topic_feed',
        #                            body=json.dumps(data))
        # Send tweet to exchange
        self.channel.basic_publish(exchange='twitter',
                                   routing_key='',
                                   body=json.dumps(data))

        print('Sent: ', status.text.encode(sys.stdout.encoding, errors='replace'), '\n')

    def on_error(self, status_code):
        print('Encountered error with status code:', status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        print('Timeout...')
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(AUTH, CustomStreamListener(api))
sapi.filter(track=['starbucks'])
