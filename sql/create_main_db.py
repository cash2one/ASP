#!/usr/bin/env python3
import os
import sqlite3

def create_table(db):
  with sqlite3.connect(db) as con:
    cur = con.cursor()

    sql = '''
    CREATE TABLE IF NOT EXISTS crawl_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      site TEXT,
      date DATE,
      year INTEGER,
      woy  INTEGER
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE IF NOT EXISTS green_rank (
      date DATE,
      rank INTEGER,
      keyword TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE IF NOT EXISTS display_rank (
      date DATE,
      rank INTEGER,
      keyword TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE IF NOT EXISTS weekly_comment (
      date DATE,
      comment TEXT
    )
    '''
    cur.execute(sql)


if __name__ == '__main__':
  # Pathの決定
  home = os.environ.get('ASP_HOME', '/home/asp')

  db = home + '/db/main.sqlite3'

  create_table(db)

