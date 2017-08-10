#!/usr/bin/env python3
import sqlite3
import os
import datetime

import jinja2

home = os.environ.get('ASP_HOME', '/home/asp')

env = jinja2.Environment(loader=jinja2.FileSystemLoader(home + '/www/admin/webApp/templates/', encoding='utf-8'))

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

  
def get_rank_comment():
  tm = datetime.datetime.utcnow() + datetime.timedelta(hours=9)

  date = datetime.date(year=tm.year, month=tm.month, day=tm.day)
  
  db = home + '/db/main.sqlite3'
  rank = []
  rank_pos = [{'name': '殿堂',
               'rank': [
                 {'rank': 'same', 'keyword': '世界'},
                 {'rank': 'same', 'keyword': 'しませんか'},
                 {'rank': 'same', 'keyword': '一緒'},
                 {'rank': 'same', 'keyword': '成長'},
                 {'rank': 'same', 'keyword': '活躍'},
                 {'rank': 'same', 'keyword': 'お任せします'},
                 {'rank': 'same', 'keyword': '環境'},
                 {'rank': 'same', 'keyword': '経験'},
               ]
             }]
  names = {
    'engineer': 'エンジニア系',
    'designer': 'デザイナー系',
    'sales': '営業系',
    'consul': 'コンサルタント系',
    'other': 'その他',
    'change': '新規急上昇',
  }
  
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()
    
    sql = '''
    SELECT
     rank,
     last_rank,
     keyword
    FROM
     display_rank
    WHERE
     date = ?
    ORDER BY rank
    LIMIT 5;
    '''
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    for r in rows:
      if r['rank'] <= 5:
        if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
          rank.append({'rank': 'up', 'keyword': r['keyword']})
        elif r['last_rank'] < r['rank']:
          rank.append({'rank': 'down', 'keyword': r['keyword']})
        else:
          rank.append({'rank': 'same', 'keyword': r['keyword']})        
      else:
        break
    for p in ['change', 'engineer', 'designer', 'sales', 'consul']:
      rr = {'name': names[p],
            'rank': []
      }
      sql = '''
      SELECT
       rank,
       last_rank,
       keyword
      FROM
       display_rank_{}
      WHERE
       date = ?
      ORDER BY rank
      LIMIT 5;
      '''
      sql = sql.format(p)
      cur.execute(sql, (date,))
      
      rows = cur.fetchall()
      if p == 'change':
        for r in rows:
          if r['rank'] <= 5:
            rr['rank'].append({'rank': 'up', 'keyword': r['keyword']})
          else:
            break
      else:
        for r in rows:
          if r['rank'] <= 5:
            if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
              rr['rank'].append({'rank': 'up', 'keyword': r['keyword']})
            elif r['last_rank'] < r['rank']:
              rr['rank'].append({'rank': 'down', 'keyword': r['keyword']})
            else:
              rr['rank'].append({'rank': 'same', 'keyword': r['keyword']})        
          else:
            break
      rank_pos.append(rr)
      
        
    sql = '''
    SELECT
     comment
    FROM
     weekly_comment
    WHERE
     date = ?
    '''
    cur.execute(sql, (date, ))
    f = cur.fetchone()
    if f is None:
      comment = None
    else:
      comment = f['comment']

    if len(rank) == 0:
      rank = None
  return rank, rank_pos, comment
  
if __name__ == '__main__':
  rank, rank_pos, comment = get_rank_comment()
  if rank is not None:
    tpl = env.get_template('common.js')
    common_js = home + '/www/public/js/common.js'
    
    page = {'rank': rank,
            'comment': comment}
    msg = tpl.render(page=page)
    with open(common_js, 'w') as f:
      f.write(msg)

    tpl = env.get_template('index.html')
    index_html = home + '/www/public/index.html'
    msg = tpl.render(ranking=rank_pos)
    with open(index_html, 'w') as f:
      f.write(msg)

    tpl = env.get_template('error.html')
    error_html = home + '/www/public/error.html'
    msg = tpl.render(ranking=rank_pos)
    with open(error_html, 'w') as f:
      f.write(msg)
      
    tm = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    date = datetime.date(year=tm.year, month=tm.month, day=tm.day)
  
    db = home + '/db/main.sqlite3'
    rank = []
    with sqlite3.connect(db) as con:
      con.row_factory = dict_factory
      cur = con.cursor()

      sql = '''INSERT INTO public_date (date) VALUES (?); '''
      cur.execute(sql, (date, ))
      con.commit()

      
