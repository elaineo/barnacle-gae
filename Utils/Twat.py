from birdy.twitter import UserClient
from google.appengine.ext import ndb

import json
import logging

twitter_handle = 'GoBarnacle'
CONSUMER_KEY = 'eSdLTYTrltusULbDvoU0A'
CONSUMER_SECRET = 'P1vCmdiHJ2fMZUdSrTB8VoSYxsPzI6fePOl35KwrLU'
ACCESS_TOKEN = '1698640628-6YKNvQZKslGrIHLsM5tWQYrqNjpXQczAVkfQPZH'
ACCESS_TOKEN_SECRET = 'mtjDvYZqFPcKlmeZv9R29xntNWmLJYV6aNMRMeTy8Mese'

def fetch_twitter():
    client = UserClient(CONSUMER_KEY,
                    CONSUMER_SECRET,
                    ACCESS_TOKEN,
                    ACCESS_TOKEN_SECRET)
    response = client.api.users.show.get(screen_name=twitter_handle)
    logging.info(response.data)