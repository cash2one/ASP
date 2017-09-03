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

  rank_t = []
  for r in k:
    if r['rank'] <= 5:
      if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
        rank_t.append({'rank': 'up', 'keyword': r['keyword'], 'no': r['rank']})
      elif r['last_rank'] < r['rank']:
        rank_t.append({'rank': 'down', 'keyword': r['keyword'], 'no': r['rank']})
      else:
        rank_t.append({'rank': 'same', 'keyword': r['keyword'], 'no': r['rank']})        
    else:
      break
  
  rank = [{'name': '殿堂',
           'rank': [
             {'rank': 'same', 'keyword': '世界'},
             {'rank': 'same', 'keyword': 'しませんか'},
             {'rank': 'same', 'keyword': '一緒'},
             {'rank': 'same', 'keyword': '成長'},
             {'rank': 'same', 'keyword': '活躍'},
             {'rank': 'same', 'keyword': 'お任せします'},
             {'rank': 'same', 'keyword': '環境'},
             {'rank': 'same', 'keyword': '経験'},
             {'rank': 'same', 'keyword': 'ui'},
             {'rank': 'same', 'keyword': '設計'},
             {'rank': 'same', 'keyword': '技術'},
             {'rank': 'same', 'keyword': '挑戦'},
             {'rank': 'same', 'keyword': '運用'},
             {'rank': 'same', 'keyword': '急成長'},
             {'rank': 'same', 'keyword': '新規事業'},             
             {'rank': 'same', 'keyword': 'ベンチャー'},
             {'rank': 'same', 'keyword': 'サービス'},
             {'rank': 'same', 'keyword': '未経験'},
             {'rank': 'same', 'keyword': '残業'},
             {'rank': 'same', 'keyword': 'php'},
             {'rank': 'same', 'keyword': '東京勤務'},
           ]
           }]
  names = {
    'engineer': 'エンジニア系',
    'designer': 'デザイナー系',
    'sales': '営業系',
    'consul': 'コンサルタント系',
    'other': 'その他',
    'change': '新規注目'
  }
  
  for p in ['change', 'engineer', 'designer', 'sales', 'consul']:
    rr = {'name': names[p],
          'rank': []
    }
    if p == 'change':
      for r in k2[p]:
        if r['rank'] <= 5:
          rr['rank'].append({'rank': 'up', 'keyword': r['keyword'], 'no': r['rank']})
        else:
          break
    else:
      for r in k2[p]:
        if r['rank'] <= 5:
          if r['last_rank'] == '-' or r['last_rank'] > r['rank']:
            rr['rank'].append({'rank': 'up', 'keyword': r['keyword'], 'no': r['rank']})
          elif r['last_rank'] < r['rank']:
            rr['rank'].append({'rank': 'down', 'keyword': r['keyword'], 'no': r['rank']})
          else:
            rr['rank'].append({'rank': 'same', 'keyword': r['keyword'], 'no': r['rank']})        
        else:
          break
    rank.append(rr)
  models.template.render_json(rank_t, rank, comment)        
  models.template.render_each(rank)
