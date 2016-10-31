# -*- coding: utf-8 -*-

import sqlite3
import os

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def get_rank(db, limit=1500):
  ret = []

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

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
      ret.append({'rank': r['rank'], 'keyword': r['keyword'], 'point': r['point'], 'no': r['rowid']})
  return ret
