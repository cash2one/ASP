# -*- coding: utf-8 -*-
import sqlite3
import os

pos_kind = ['engineer', 'designer', 'sales', 'consul', 'other']

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

def get_latest_rank():
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  ret = []

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    SELECT
     distinct date
    FROM
     public_date
    ORDER BY date DESC
    LIMIT 1
    '''

    cur.execute(sql)
    date = cur.fetchone()['date']

    sql = '''
    SELECT
      rank,
      keyword
    FROM
      display_rank
    WHERE
      date = ?
    '''
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    rank = {}
    for r in rows:
      print(r['keyword'], r['rank'])
      rank[r['keyword']] = r['rank']

    return rank

def get_latest_rank_pos(pos):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  ret = []

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    SELECT
     distinct date
    FROM
     public_date
    ORDER BY date DESC
    LIMIT 1
    '''

    cur.execute(sql)
    date = cur.fetchone()['date']

    sql = '''
    SELECT
      rank,
      keyword
    FROM
      display_rank_{}
    WHERE
      date = ?
    '''
    sql = sql.format(pos)
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    rank = {}
    for r in rows:
      print(r['keyword'], r['rank'])
      rank[r['keyword']] = r['rank']

    return rank

    
def remove_comment(tm):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'
  
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    DELETE FROM
     weekly_comment
    WHERE
     date = ?
    '''
    cur.execute(sql, (tm,))
    con.commit()

def remove_ranking(tm):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'
  
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    DELETE FROM
     display_rank
    WHERE
     date = ?
    '''
    cur.execute(sql, (tm,))

    for p in pos_kind:
      sql = '''
      DELETE FROM
       display_rank_{}
      WHERE
       date = ?
      '''
      sql = sql.format(p)
      cur.execute(sql, (tm,))
    
    con.commit()
    
def save_comment(tm, comment):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    INSERT INTO
      weekly_comment (date, comment)
    VALUES
      (?, ?)
    '''
    cur.execute(sql, (tm, comment))
    con.commit()

def save_ranking(tm, ranking):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    INSERT INTO
      display_rank (date, rank, last_rank, keyword)
    VALUES
      (?, ?, ?, ?)
    '''

    for r in ranking:
      cur.execute(sql, (tm, r['rank'], r['last_rank'], r['keyword']))
    con.commit()
  
def save_ranking_pos(tm, ranking):
  home = os.environ.get('ASP_HOME', '/home/asp')
  db = home + '/db/main.sqlite3'

  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    for p in ranking:
      sql = '''
      INSERT INTO
        display_rank_{} (date, rank, last_rank, keyword)
      VALUES
        (?, ?, ?, ?)
      '''
      sql = sql.format(p)
      for r in ranking[p]:
        cur.execute(sql, (tm, r['rank'], r['last_rank'], r['keyword']))
    con.commit()
  
