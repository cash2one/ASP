# -*- coding: utf-8 -*-
import webApp.models as models
from . import keywords 

def save_ranking(tm, comment):
  k = keywords.get_total_rank()
  k2 = keywords.get_pos_rank()
  
  models.maindb.remove_comment(tm)
  models.maindb.remove_ranking(tm)
  
  models.maindb.save_comment(tm, comment)  
  models.maindb.save_ranking(tm, k)
  models.maindb.save_ranking_pos(tm, k2)

  rank = []
  for r in k:
    if r['rank'] <= 5:
      if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
        rank.append({'rank': 'up', 'keyword': r['keyword']})
      elif r['last_rank'] < r['rank']:
        rank.append({'rank': 'down', 'keyword': r['keyword']})
      else:
        rank.append({'rank': 'same', 'keyword': r['keyword']})        
    else:
      break
  
  models.template.render_json(rank, comment)

  rank = [{'name': '殿堂',
           'rank': [
             {'rank': 'same', 'keyword': '世界'},
             {'rank': 'same', 'keyword': 'しませんか'},
             {'rank': 'same', 'keyword': '一緒'},
             {'rank': 'same', 'keyword': '成長'},
             {'rank': 'same', 'keyword': '活躍'},
           ]
           }]
  names = {
    'engineer': 'エンジニア系',
    'designer': 'デザイナー系',
    'sales': '営業系',
    'consul': 'コンサルタント系',
    'other': 'その他',
  }
  
  for p in ['engineer', 'designer', 'sales', 'consul', 'other']:
    rr = {'name': names[p],
          'rank': []
    }
    for r in k2[p]:
      if r['rank'] <= 5:
        if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
          rr['rank'].append({'rank': 'up', 'keyword': r['keyword']})
        elif r['last_rank'] < r['rank']:
          rr['rank'].append({'rank': 'down', 'keyword': r['keyword']})
        else:
          rr['rank'].append({'rank': 'same', 'keyword': r['keyword']})        
      else:
        break
    rank.append(rr)
        
  models.template.render_each(rank)
