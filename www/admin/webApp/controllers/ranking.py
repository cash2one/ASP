# -*- coding: utf-8 -*-
import webApp.models as models
from . import keywords 

def save_ranking(tm, comment):
  k = keywords.get_total_rank()

  models.maindb.remove_comment(tm)
  models.maindb.remove_ranking(tm)
  
  models.maindb.save_comment(tm, comment)  
  models.maindb.save_ranking(tm, k)

  rank = []
  for r in k:
    if r['rank'] <= 5:
      if r['last_rank'] == '-' or r['last_rank'] == r['rank']:
        rank.append({'rank': 'same', 'keyword': r['keyword']})
      elif r['last_rank'] < r['rank']:
        rank.append({'rank': 'down', 'keyword': r['keyword']})
      else:
        rank.append({'rank': 'up', 'keyword': r['keyword']})        
    else:
      break
  
  models.template.render_json(rank, comment)
  models.template.render_each(rank)
