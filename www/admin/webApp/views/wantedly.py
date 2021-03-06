# -*- coding: utf-8 -*-

import flask
from webApp import app

import webApp.controllers as controllers

@app.route('/Wantedly', methods=['GET', 'POST'])
def views_wantedly():
  if flask.request.method == 'GET':
    keywords = controllers.keywords.get("wantedly")
    date_id = -1
  elif flask.request.method == 'POST':
    print(flask.request.form['history'])
    try:
      date_id = int(flask.request.form['history'])
    except:
      flask.abort(500)
    keywords = controllers.keywords.get_with_date("wantedly", date_id)
  date_list = controllers.crawler.get_history("wantedly")
  page = {
    "page": "Wantedly",
    "title": "Wantedlyのキーワード",
    "keywords": keywords,
    "histories": date_list,
    "date_id": date_id
  }
  return flask.render_template('each_keyword.html', page=page)

  
@app.route('/save_Wantedly', methods=['POST'])
def views_wantedly_save():
  print(flask.request.form)
  return flask.redirect(flask.url_for('views_wantedly'))
