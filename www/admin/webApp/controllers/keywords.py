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
    
def get_total_rank():
  r = models.maindb.crawl_history("green", 1)
  green_keyword = models.sitedb.get_rank(r[0]['path'])
  r = models.maindb.crawl_history("wantedly", 1)
  wantedly_keyword = models.sitedb.get_rank(r[0]['path'])
  # {'rank': r['rank'], 'keyword': r['keyword'], 'point': r['point'], 'no': r['rowid']}

  keyword = {}
  for w in green_keyword:
    if w['keyword'] not in keyword:
      keyword[w['keyword']] = {'keyword': w['keyword'],
                               'point': 0}
    
    keyword[w['keyword']]['point'] += w['point']

  for w in wantedly_keyword:
    if w['keyword'] not in keyword:
      keyword[w['keyword']] = {'keyword': w['keyword'],
                               'point': 0}
    
    keyword[w['keyword']]['point'] += w['point']

    
  last_rank = {}
  keyword2 = models.maindb.get_latest_rank()
  for k in keyword2:
    last_rank[k] = keyword2[k]

  for k in keyword:
    keyword[k]['last_rank'] = last_rank.get(k, '-')

  r = []
  for k in keyword:
    r.append(keyword[k])
    
  ret = [] 

  prev_point = 0
  rank = 0
  i = 1
  for k in sorted(r, key=lambda x:x['point'], reverse=True):
    if prev_point != k['point']:
      rank += i
      i = 1
    else:
      i += 1
    k['rank'] = rank
    ret.append(k)
    prev_point = k['point']
    
  return ret
