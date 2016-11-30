# -*- coding: utf-8 -*-

import sqlite3
import os
import math


def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

class StdevFunc:
  def __init__(self):
    self.M = 0.0
    self.S = 0.0
    self.k = 1
    
  def step(self, value):
    if value is None:
      return
    tM = self.M
    self.M += (value - tM) / self.k
    self.S += (value - tM) * (value - self.M)
    self.k += 1
    
  def finalize(self):
    if self.k < 3:
      return None
    return math.sqrt(self.S / (self.k-2))
  
def get_rank(db, limit=1500):
  ret = []

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    con.create_aggregate("stdev", 1, StdevFunc)
    cur = con.cursor()

    sql = '''
    SELECT
      avg(point) AS avg,
      stdev(point) AS sd
    FROM
     raw_ranking
    '''
    cur.execute(sql)
    r = cur.fetchone()
    avg = r['avg']
    sd = r['sd']
    
    sql = '''
    SELECT
      rowid,
      rank,
      keyword,
      point
    FROM
      raw_ranking
    WHERE
      rank <= ?
    '''
    cur.execute(sql, (limit, ))

    rows = cur.fetchall()
    for r in rows:
      ret.append({'rank': r['rank'], 'keyword': r['keyword'], 'point': 10.*(r['point'] - avg) / sd + 50, 'no': r['rowid']})
  return ret

def get_title(db):
  ret = []

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    con.create_aggregate("stdev", 1, StdevFunc)
    cur = con.cursor()

    sql = '''
    SELECT
      title
    FROM
      offer
    '''
    cur.execute(sql)

    rows = cur.fetchall()
    for r in rows:
      ret.append({'title': r['title']})
  return ret
