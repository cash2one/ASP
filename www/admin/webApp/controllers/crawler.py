# -*- coding: utf-8 -*-
import webApp.models as models


def get_history(site):
  r = models.maindb.crawl_history(site)
  return r

def get_title(site):
  r = models.maindb.crawl_history(site, 1)
  keyword = models.sitedb.get_title(r[0]['path'])

  return keyword

def get_title_with_date(site, date_id):
  db = models.maindb.crawl_db(site, date_id)
  keyword = models.sitedb.get_title(db['path'])

  return keyword
  
