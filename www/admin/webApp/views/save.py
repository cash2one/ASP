# -*- coding: utf-8 -*-

import flask
from webApp import app
import datetime

import webApp.controllers as controllers

@app.route('/save_total', methods=['POST'])
def display_save_total():
  comment = flask.request.form['hitokoto']
  comment = comment.replace('\n', '')
  comment = comment.replace('\r', '')  
  year = flask.request.form['year']
  month = flask.request.form['month']
  day = flask.request.form['day']

  tm = datetime.date(year=int(year), month=int(month), day=int(day))

  controllers.ranking.save_ranking(tm, comment)

  return flask.redirect('http://staging.圧倒的成長.com/')
