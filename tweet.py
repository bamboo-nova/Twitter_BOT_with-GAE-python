#! -*- coding: utf-8 -*-
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from django.utils.simplejson import loads

import webapp2, tweepy
from datetime import datetime
import logging
import config

from launcher import modelTask
from main import modelUser

RIOT_KEY = config.RIOT_KEY

class mainHandler(webapp2.RequestHandler):
  def post(self):
    getGame((self.request.get('qid')))

def getGame(qid):
  q = modelTask().get_by_id(qid, parent=None)
  # あるサモナーの試合リストを表示させる
  matches = urlfetch.fetch('https://'+q.region+'.api.riotgames.com/lol/match/v4/matchlists/by-account/'+str(q.accountId)+'?api_key='+RIOT_KEY)
  if matches.status_code == 200:
    # APIから取得した各種値をセットする(最新のマッチング試合情報を取り出す)
    game = loads(matches.content)['matches'][0]['gameId']
  result = urlfetch.fetch('https://'+q.region+'.api.riotgames.com/lol/match/v4/matches/'+str(game)+'?api_key='+RIOT_KEY)
  if result.status_code == 200:
    members = loads(result.content)['participantIdentities']

  i=0
  lists=[]
  try:
    for m in members:
      name = m['player']['summonerName']
      if i<5:
        lists.append(name)
      i=i+1
  except:
    lists = '一緒に戦った参加者はいません'
  lists = ','.join(lists)
    
  message = q.summoner_name+u'さんが直近で対戦した試合では、...'+lists+u'などが参加されています'
  if tweet(message, q.access_key, q.access_secret):
    logging.info(u'ok')

# Twitter投稿処理
def tweet(message, access_key, access_secret):
  try:
    auth = tweepy.OAuthHandler(config.TWITTER_CREDENTIALS['CONSUMER_KEY'],config.TWITTER_CREDENTIALS['CONSUMER_SECRET'])
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    api.update_status(status=message)
    return True
  except:
    return False

app = webapp2.WSGIApplication([ ('/tweet', mainHandler) ])


   
    
