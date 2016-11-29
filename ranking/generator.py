#!/usr/bin/env python3
import argparse
import os
import sqlite3

synonymous_word = {}
negative_word = []
ranking = {}

def read_synonymous_word():
  fp = os.environ.get('ASP_HOME', '/home/asp') + '/dic/synonymous.txt'
  with open(fp, 'r', encoding='utf-8') as f:
    for l in f:
      l = l.strip()
      words = l.split(',')
      for w in words[1:]:
        synonymous_word[w] = words[0]

def read_negative_word():
  fp = os.environ.get('ASP_HOME', '/home/asp') + '/dic/negative.txt'
  with open(fp, 'r', encoding='utf-8') as f:
    for l in f:
      l = l.strip()
      negative_word.append(l)

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def setup_database(db_name):
  with sqlite3.connect(db_name) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''DROP TABLE IF EXISTS raw_ranking; '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE raw_ranking (
      rank INTEGER,
      keyword TEXT,
      point INTEGER
    )
    '''
    cur.execute(sql)

  
def generate_ranking(db_name):
  with sqlite3.connect(db_name) as con:
    con.row_factory = dict_factory
    cur = con.cursor()
  
    sql = '''SELECT keyword, cnt FROM (SELECT keyword_id, COUNT(1) AS cnt FROM offer_keywords GROUP BY keyword_id) t1 INNER JOIN keywords t2 ON t1.keyword_id = t2.id ORDER BY cnt DESC;'''
    cur.execute(sql)

    rows = cur.fetchall()
    for r in rows:
      if r['keyword'] in negative_word:
        print(r['keyword'])
        continue
      if r['keyword'] in synonymous_word:
        s = synonymous_word[r['keyword']]
        if s in negative_word:
          print(r['keyword'], s)
          continue
        r['keyword'] = s
      if r['keyword'] in ranking:
        ranking[r['keyword']] += r['cnt']
      else:
        ranking[r['keyword']] = r['cnt']

    rank = 0
    i = 1
    prev_point = 0
    for word, point in sorted(ranking.items(), key=lambda x:x[1],reverse=True):
      if word in negative_word:
        print(word)
        continue
      if prev_point != point:
        rank += i
        i = 1
      else:
        i += 1
      if rank > 200:
        break
      sql = ''' INSERT INTO raw_ranking (rank, keyword, point) VALUES (?, ?, ?); '''
      cur.execute(sql, (rank, word, point))
      prev_point = point
    con.commit()
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Ranking generator')
  parser.add_argument('db', metavar='DB', type=str, help='DataBase Name')

  args = parser.parse_args()

  read_synonymous_word()
  read_negative_word()

  setup_database(args.db)
  generate_ranking(args.db)
