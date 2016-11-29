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
  return rank, comment
  
if __name__ == '__main__':
  rank, comment = get_rank_comment()
  if rank is not None:
    tpl = env.get_template('common.js')
    common_js = home + '/www/public/js/common.js'
    
    page = {'rank': rank,
            'comment': comment}
    msg = tpl.render(page=page)
    with open(common_js, 'w') as f:
      f.write(msg)
                         
    
