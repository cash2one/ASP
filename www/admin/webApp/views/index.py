# -*- coding: utf-8 -*-

import flask
from webApp import app

import webApp.controllers as controllers

@app.route('/index')
def views_index():
  return "OK"

@app.route('/Green', methods=['GET', 'POST'])
def views_green():
  if flask.request.method == 'GET':
    keywords = controllers.keywords.get("green")
  elif flask.request.method == 'POST':
    print(flask.request.form['history'])
    try:
      date_id = int(flask.request.form['history'])
    except:
      flask.abort(500)
    keywords = controllers.keywords.get_with_date("green", date_id)
  date_list = controllers.crawler.get_history("green")
  page = {
    "page": "Green",
    "title": "Greenのキーワード",
    "keywords": keywords,
    "histories": date_list,
  }
  return flask.render_template('each_keyword.html', page=page)

  
@app.route('/save_Green', methods=['POST'])
def views_green_save():
  return flask.redirect(flask.url_for('views_green'))
