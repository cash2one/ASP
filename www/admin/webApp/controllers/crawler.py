# -*- coding: utf-8 -*-
import webApp.models as models


def get_history(site):
  r = models.maindb.crawl_history(site)
  return r
