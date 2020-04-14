#! -*- coding: utf-8 -*-
from google.appengine.api import taskqueue
import webapp2
from google.appengine.ext import ndb
from google.appengine.api.backends import get_backend
import logging


class modelTask(ndb.Model): # キューに入れるタスク
  region = ndb.StringProperty()
  summoner_name = ndb.StringProperty()
  summoner_id = ndb.StringProperty()
  accountId = ndb.StringProperty()
  access_key = ndb.StringProperty()
  access_secret = ndb.StringProperty()
  date = ndb.DateTimeProperty(auto_now_add=True)
  date_success = ndb.DateTimeProperty(auto_now_add=True)

class mainHandler(webapp2.RequestHandler):
  def get(self):
    qs = modelTask.query().fetch()
    if target is None: # Backendで起動されていればTaskQueueも同様に
      for q in qs: # タスクを全てQueueに追加する
        if q.accountId is not None:
          taskqueue.add(queue_name='tweet', url='/tweet', params={'qid': q.key.id()})
    else:
      for q in qs:
        taskqueue.add(queue_name='tweet', url='/tweet', params={'qid': q.key().id()}, target='tweet')

class WarmupHandler(webapp2.RequestHandler): # Backend起動時に強制的に呼び出される 
  def index(self):
    logging.info('warmup done')

app = webapp2.WSGIApplication([ ('/launcher', mainHandler),('/_ah/warmup', WarmupHandler) ])