# -*- coding: utf-8 -*-
import sqlite3
import os

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def crawl_history(site, limit=5):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  ret = []
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    SELECT
      ROWID,
      date,
      path
    FROM
      crawl_history
    WHERE
      site = ?
    ORDER BY id DESC
    LIMIT ?
    '''
    cur.execute(sql, (site, limit))
    rows = cur.fetchall()

    for row in rows:
      ret.append({'id': row['id'], 'date': row['date'], 'path': row['path']})
  return ret

def crawl_db(site, rowid):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  ret = []
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    SELECT
      path
    FROM
      crawl_history
    WHERE
      site = ?
    AND
      ROWID = ?
    '''
    cur.execute(sql, (site, rowid))
    rows = cur.fetchall()

    for row in rows:
      ret.append({'path': row['path']})

  if len(ret) == 0:
    return None
  else:
    return ret[0]
