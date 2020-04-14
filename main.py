#! -*- coding: utf-8 -*-
from google.appengine.api import urlfetch
from django.utils.simplejson import loads


from google.appengine.ext import ndb
import webapp2, tweepy
import requests
import jinja2
import os
import requests_toolbelt.adapters.appengine
import twitter

from urllib import quote
from time import mktime
from cgi import escape
from datetime import datetime

import config
from launcher import modelTask


NAME = config.TWITTER_NAME # Twitter name 
RIOT_KEY = config.RIOT_KEY

requests_toolbelt.adapters.appengine.monkeypatch()

JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True)

class modelUser(ndb.Model): # Twitterアカウント情報格納のモデル定義
  twitter_name = ndb.StringProperty()
  access_key = ndb.StringProperty()
  access_secret = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)

class mainHandler(webapp2.RequestHandler):
  def get(self):
    # 認証開始ボタンを出力
    self.response.out.write('''
        <form method="POST" action="./">
            <button type="submit">認証</button>
        </form>
        ''')
  def post(self):
    print(config.TWITTER_CREDENTIALS)
    auth = tweepy.OAuthHandler(config.TWITTER_CREDENTIALS['CONSUMER_KEY'],config.TWITTER_CREDENTIALS['CONSUMER_SECRET'])
    try:
      redirect_url = auth.get_authorization_url() #OAuth認証用URLを取得
      self.redirect(str(redirect_url)) #OAuth認証用URLにリダイレクト
    except Exception as e:
      self.response.out.write('エラー')


class callbackHandler(webapp2.RequestHandler):
  def get(self):
    try:
      #なんか受け取ったパラメタをTweepyに色々と認証させる
      verifier = self.request.get('oauth_verifier')
      auth = tweepy.OAuthHandler(config.TWITTER_CREDENTIALS['CONSUMER_KEY'],config.TWITTER_CREDENTIALS['CONSUMER_SECRET'])
      auth.request_token
      token = self.request.get('oauth_token')
      auth.request_token = { 'oauth_token' : token,
                         'oauth_token_secret' : verifier }
      try:
        auth.get_access_token(verifier)
      except tweepy.TweepError:
        print('Error! Failed to get access token.')
            
      access_key = auth.access_token
      access_secret = auth.access_token_secret
      auth.set_access_token(access_key, access_secret)
      api = tweepy.API(auth) #以降、このオブジェクトから色々情報を取得できる

      modeluser = modelUser().get_or_insert(str(api.me().id)) #モデルキーをTwitter内部IDに設定
      modeluser.twitter_name = api.me().screen_name #Twitter Id
      modeluser.access_key = access_key #アクセストークンキー
      modeluser.access_secret = access_secret #アクセスシークレットトークンキー
      modeluser.put() #データベースに反映

      # print(api.me().screen_name) # NAMEを調べるための検証用
      self.redirect('/registration')
    except Exception as e:
      self.response.out.write('エラ')

def getId(region, summoner_name):
  # APIからサモナー情報を取得する
  result = urlfetch.fetch('https://'+region+'.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+quote(summoner_name)+'?api_key='+RIOT_KEY)
  if result.status_code == 200:
    # JSONパーサへ渡してIDと名前を返す
    result = loads(result.content)
    return result[u'id'], result[u'name'], result[u'accountId']
  else:
    return -1, None

class registrationHandler(webapp2.RequestHandler):
  def get(self):
    # サモナー名を入力して、APIから自分のゲームIDなどを取得してndbへ保存する
    self.response.out.write('''登録完了
    <form method="POST" action="./registration">
      <input type="radio" name="region" value="1" checked="checked" />NA
      <input type="radio" name="region" value="2" />JP1
      <input type="radio" name="region" value="3" />EUNE
      <input type="text" name="summoner_name" />
      <button type="submit">取得</button>
    </form>''')
  def post(self):
    try:
      # 入力された名前とリージョンを取得
      summoner_name = escape(self.request.get('summoner_name'))
      if escape(self.request.get('region')) == '1':
        region = 'na'
      elif escape(self.request.get('region')) == '2':
        region = 'jp1'
      elif escape(self.request.get('region')) == '3':
        region = 'eune'
            
      # サモナーID取得関数を呼び出す
      summoner_id, summoner_name, accountId = getId(region, summoner_name)

      # ndbへ保存する
      query = modelUser.query(ndb.AND(modelUser.twitter_name == NAME))
      user = query.get()
      modeltask = modelTask().get_or_insert(summoner_id) # ここの名前はお好みで
      modeltask.access_key = str(user.access_key)
      modeltask.access_secret = str(user.access_secret)
      modeltask.region = region
      modeltask.summoner_id = summoner_id
      modeltask.summoner_name = summoner_name
      modeltask.accountId = accountId
      modeltask.put()

      # 結果を出力する
      if len(summoner_id)>0:
        self.response.out.write(u'サモナーID: '+summoner_id+u'サモナー名: '+summoner_name)
      else:
        self.response.out.write('サモナーが存在しない')
        return
            
    except Exception as e:
      self.response.out.write('エラー') 

app = webapp2.WSGIApplication([ ('/', mainHandler), ('/callback', callbackHandler), ('/registration', registrationHandler)])




