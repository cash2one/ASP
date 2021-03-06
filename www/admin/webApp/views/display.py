# -*- coding: utf-8 -*-

import flask
from webApp import app

import webApp.controllers as controllers

@app.route('/display', methods=['GET', 'POST'])
def views_display():
  if flask.request.args.get('action', None) == 'determine':
    keywords = controllers.keywords.get_total_rank()
    positions = controllers.keywords.get_pos_rank()
    
    page = {'page': 'total',
            'keywords': keywords,
            'positions': positions
          }
  else:
    page = {'page': None}
  return flask.render_template('display.html', page=page)
