# -*- coding: utf-8 -*-

import flask
from webApp import app
import datetime

import webApp.controllers as controllers

@app.route('/save_total', methods=['POST'])
def display_save_total():
  comment = flask.request.form['hitokoto']
  year = flask.request.form['year']
  month = flask.request.form['month']
  day = flask.request.form['day']

  tm = datetime.date(year=int(year), month=int(month), day=int(day))

  controllers.ranking.save_ranking(tm, comment)

  return flask.redirect('http://staging-asp.nne4fine.net/')
