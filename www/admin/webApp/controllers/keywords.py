# -*- coding: utf-8 -*-
import datetime

import webApp.models as models

def get(site):
  r = models.maindb.crawl_history(site, 2)
  #r = [{'date': datetime.date(year=2016, month=10, day=22), 'path': '/home/kawasaki/asp/db/green_2016_42.sqlite3'}]

  keyword1 = models.sitedb.get_rank(r[0]['path'])

  if len(r) == 2:
    keyword2 = models.sitedb.get_rank(r[1]['path'])
  else:
    keyword2 = []

  last_rank = {}
  for k in keyword2:
    last_rank[k['keyword']] = k['rank']

  ret = []
  for k in keyword1:
    k['last_rank'] = last_rank.get(k['keyword'], '-')
    ret.append(k)

  return ret

def get_with_date(site, date_id):
  db = models.maindb.crawl_db(site, date_id)
  keyword1 = models.sitedb.get_rank(db['path'])
  if date_id > 1:
    db = models.maindb.crawl_db(site, date_id - 1)
    keyword2 = models.sitedb.get_rank(db['path'])
  else:
    keyword2 = []
  last_rank = {}
  for k in keyword2:
    last_rank[k['keyword']] = k['rank']

  ret = []
  for k in keyword1:
    k['last_rank'] = last_rank.get(k['keyword'], '-')
    ret.append(k)

  return ret
    
