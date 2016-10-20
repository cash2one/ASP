#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import re
import sqlite3
import argparse

import mysql.connector
import MeCab


_re_num = re.compile('[\d,]+')
independece_word = []
stop_word = []

def read_independece_word():
  fp = os.environ.get('ASP_HOME', '/home/asp') + '/dic/independece.txt'
  with open(fp, 'r', encoding='utf-8') as f:
    for l in f:
      l = l.strip()
      independece_word.append(l)

def read_stop_word():
  fp = os.environ.get('ASP_HOME', '/home/asp') + '/dic/stop.txt'
  with open(fp, 'r', encoding='utf-8') as f:
    for l in f:
      l = l.strip()
      stop_word.append(l)

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d
      
      
def extractor(db_name):
  with sqlite3.connect(db_name) as con:
    con.row_factory = dict_factory
    cur = con.cursor()
    
    sql = ''' SELECT id, title FROM offer; '''

    cur.execute(sql)

    rows = cur.fetchall()
    for r in rows:
      offer_id = r['id']
      words = get_words(r['title'])
      keywords = []
      p = None
      w = ""
      for word, PoS in words:
        #if PoS not in ['BOS/EOS', '名詞', '助詞', '記号', '動詞', '接頭詞']:
        #  print("  ", word, PoS)
        if _re_num.search(word) is not None:
          if len(w) not in [0, 1] and w not in stop_word:
            keywords.append(w.lower())
            p = None
            w = ""
        if PoS in ['記号', 'BOS/EOS']:
          if len(w) not in [0, 1] and w not in stop_word:
            keywords.append(w.lower())
            p = None
            w = ""
          else:
            p = None
            w = ""
          continue
        if PoS == p == '名詞':
          if word in ['x', 'X', 'ｘ', '×']:
            if len(w) not in [0, 1]:
              keywords.append(w.lower())
            p = None
            w = ""
          elif word in independece_word:
            if len(w) not in [0, 1] and w not in stop_word:
              keywords.append(w.lower())
              keywords.append(word.lower())
            p = None
            w = ""
          else:
            w += word
        elif PoS in ['名詞', '連体詞', '助動詞']:
          if word in independece_word:
            if len(word) not in [0, 1] and w not in stop_word:
              keywords.append(word.lower())
            p = None
            w = ""
          else:
            if PoS != '助動詞':
              w += word
              p = '名詞'
            else:
              if word == 'な':
                w += word
                p = '名詞'
              else:
                if len(w) not in [0, 1] and w not in stop_word:
                  keywords.append(w.lower())
                w = ""
                p = None
        elif PoS == '助詞':
          if w != "":
            if len(w) not in [0, 1] and w not in stop_word:
              keywords.append(w.lower())
          w = ""
          p = None
        else:
          if len(w) not in [0, 1] and w not in stop_word:
            keywords.append(w.lower())
          w = ""
          p = None
        p = PoS
      print(offer_id, keywords)
      save_database(offer_id, keywords, cur)
    con.commit()
  
def save_database(offer_id, keywords, cur):
  for tag in keywords:
    cur.execute('''SELECT id FROM keywords WHERE keyword = ?; ''', (tag,))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO keywords (keyword) VALUES (?); ''', (tag,))
      cur.execute('''SELECT id FROM keywords WHERE keyword = ?; ''', (tag,))
      r = cur.fetchone()
    tag_id = r['id']
          
    cur.execute('''SELECT id FROM offer_keywords WHERE offer_id = ? AND keyword_id = ?; ''', (offer_id, tag_id))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO offer_keywords (offer_id, keyword_id) VALUES (?, ?); ''', (offer_id, tag_id))
      cur.execute('''SELECT id FROM offer_keywords WHERE offer_id = ? AND keyword_id = ?; ''', (offer_id, tag_id))
      r = cur.fetchone()

    
def get_words(text):
  tagger = MeCab.Tagger('-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd')  # Ubuntu
  tagger.parse('') #　おまじない(mecabのバグです)
  words = []
  node = tagger.parseToNode(text)

  while node:
    # 解析の最初に出る品詞を取得
    PoS = node.feature.split(',')[0]
    words.append((node.surface, PoS))
    node = node.next
  return words
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Keyword Extractor')
  parser.add_argument('db', metavar='DB', type=str, help='DataBase Name')

  args = parser.parse_args()

  read_independece_word()
  read_stop_word()

  extractor(args.db)
