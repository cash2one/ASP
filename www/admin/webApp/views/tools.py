# -*- coding: utf-8 -*-

import flask
from webApp import app

import webApp.controllers as controllers

@app.route('/Tools')
def views_tools():
  page = {
    "title": "Tools",
  }

  return flask.render_template('tools.html', page=page)

@app.route('/Tools/raw/title/<db>', methods=['GET', 'POST'])
def views_tools_raw_title(db):
  if flask.request.method == 'GET':
    keywords = controllers.crawler.get_title(db)
    date_id = -1
  elif flask.request.method == 'POST':
    try:
      date_id = int(flask.request.form['history'])
    except:
      flask.abort(500)
    keywords = controllers.crawler.get_title_with_date(db, date_id)
  date_list = controllers.crawler.get_history(db)
  page = {
    "page": db,
    "db": db,
    "title": db + "のTitle",
    "keywords": keywords,
    "histories": date_list,
    "date_id": date_id
  }

  return flask.render_template('raw_title.html', page=page)
