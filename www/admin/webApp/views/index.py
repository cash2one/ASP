# -*- coding: utf-8 -*-

import flask
from webApp import app

import webApp.controllers as controllers

@app.route('/')
def views_top():
  return flask.redirect(flask.url_for('views_display'))

@app.route('/index')
def views_index():
  return "OK"
