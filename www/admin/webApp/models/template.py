# -*- coding: utf-8 -*-

import flask
import sqlite3
import os

def render_json(rank, comment):
  home = os.environ.get('ASP_HOME', '/home/asp')
  common_js = home + '/www/staging/js/common.js'

  
  page = {'rank': rank,
          'comment': comment
          }
  
  msg = flask.render_template('common.js', page=page)
  with open(common_js, 'w') as f:
    f.write(msg)

def render_each(rank):
  home = os.environ.get('ASP_HOME', '/home/asp')
  index_html = home + '/www/staging/index.html'

  
  page = {}
  
  msg = flask.render_template('index.html', page=page)
  with open(index_html, 'w') as f:
    f.write(msg)
    
