# -*- coding: utf-8 -*-

import flask
import sqlite3
import os
import datetime

def render_json(rank_t, rank, comment):
  home = os.environ.get('ASP_HOME', '/home/asp')
  common_js = home + '/www/staging/js/common.js'

  
  page = {'rank': rank_t,
          'comment': comment
          }
  
  msg = flask.render_template('common.js', page=page, ranking=rank)
  with open(common_js, 'w') as f:
    f.write(msg)

def render_each(rank):
  home = os.environ.get('ASP_HOME', '/home/asp')
  index_html = home + '/www/staging/index.html'
  error_html = home + '/www/staging/error.html'
  
  page = {}
  
  msg = flask.render_template('index.html', ranking=rank, today=datetime.datetime.now().strftime('%Y%m%d'))
  with open(index_html, 'w') as f:
    f.write(msg)

  msg = flask.render_template('error.html', page=page)
  with open(error_html, 'w') as f:
    f.write(msg)
    
