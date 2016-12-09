#!/usr/bin/env python3

import time
import datetime
import re
import os
import sqlite3
import argparse

import requests
import lxml.html
from pyquery import PyQuery as pq


URL = 'https://www.wantedly.com/user/sign_in'
URL_signin = 'https://www.wantedly.com/user/sign_in'
URL_signout = 'https://www.wantedly.com/user/sign_out'
URL_project = 'https://www.wantedly.com/projects/recent'
URL_base = 'https://www.wantedly.com/projects/{}'

_re_user = re.compile('/projects/(?P<projects>[\d]+)/staffings/(?P<user>[\d]+)')

def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

def setup_database(db_name):
  with sqlite3.connect(db_name) as con:
    con.row_factory = dict_factory
    cur = con.cursor()

    sql = '''
    CREATE TABLE offer (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      wantedly_id BIGINT UNSIGNED NOT NULL,
      company_id BIGINT UNSIGNED NOT NULL,
      title TEXT NOT NULL,
      position_id BIGINT UNSIGNED NOT NULL,
      position_official_id BIGINT UNSIGNED DEFAULT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE company (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      wantedly_id TEXT UNIQUE,
      name TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE interviews (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     offer_id INTERGER,
     comment TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE position (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description TEXT NOT NULL UNIQUE
    );
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE position_official_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE
    );
    '''
    cur.execute(sql)
    
    sql = '''
    CREATE TABLE detail_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE detail (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      comment TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_detail (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      comment TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_company (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      comment TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_char_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_char (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL
    )
    '''
    cur.execute(sql)
    
    sql = '''
    CREATE TABLE apply_relation_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT UNIQUE
    )
    '''
    cur.execute(sql)
    
    sql = '''
    CREATE TABLE apply_relation (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL
    )
    '''
    cur.execute(sql)

    
def save_database(db, offer):
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()
    
    cur.execute('''SELECT id FROM company WHERE wantedly_id = ?;''', (offer['offer']['company_id'],))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO company (wantedly_id, name) VALUES (?, ?);''', (offer['offer']['company_id'], offer['offer']['company']))
      cur.execute('''SELECT id FROM company WHERE wantedly_id = ?;''', (offer['offer']['company_id'],))
      r = cur.fetchone()
    cid = r['id']

    cur.execute('''SELECT id FROM position WHERE description = ?;''', (offer['job']['kind'],))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO position (description) VALUES (?);''', (offer['job']['kind'],))
      cur.execute('''SELECT id FROM position WHERE description = ?;''', (offer['job']['kind'],))
      r = cur.fetchone()
    kid = r['id']

    if offer['job']['position'] is None:
      cur.execute('''INSERT INTO offer (wantedly_id, company_id, title, position_id) VALUES (?, ?, ?, ?)''', (offer['offer']['id'], cid, offer['offer']['title'], kid))
    else:
      cur.execute('''SELECT id FROM position_official_title WHERE name = ?;''', (offer['job']['position'],))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO position_official_title (name) VALUES (?);''', (offer['job']['position'],))
        cur.execute('''SELECT id FROM position_official_title WHERE name = ?;''', (offer['job']['position'],))
        r = cur.fetchone()
      i = r['id']
      cur.execute('''INSERT INTO offer (wantedly_id, company_id, title, position_id, position_official_id) VALUES (?, ?, ?, ?, ?)''', (offer['offer']['id'], cid, offer['offer']['title'], kid, i))
      
    cur.execute('''SELECT id FROM offer WHERE wantedly_id = ?''', (offer['offer']['id'],))
    oid = cur.fetchone()['id']
    
    for c in offer['interview']:
      cur.execute('''INSERT INTO interviews (offer_id, comment) VALUES (?, ?);''', (oid, c))


    for t in offer['details']:
      cur.execute('''SELECT id FROM detail_title WHERE title = ?;''', (t,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO detail_title (title) VALUES (?);''', (t,))
        cur.execute('''SELECT id FROM detail_title WHERE title = ?;''', (t,))
        r = cur.fetchone()
      i = r['id']

      cur.execute('''INSERT INTO detail (offer_id, title_id, comment) VALUES (?, ?, ?)''', (oid, i, offer['details'][t]))

    for t in offer['apply']:
      if t == '募集の特徴':
        for tt in offer['apply'][t]:
          cur.execute('''SELECT id FROM apply_char_title WHERE title = ?;''', (tt,))
          r = cur.fetchone()
          if r is None:
            cur.execute('''INSERT INTO apply_char_title (title) VALUES (?);''', (tt,))
            cur.execute('''SELECT id FROM apply_char_title WHERE title = ?;''', (tt,))
            r = cur.fetchone()
          i = r['id']
          cur.execute('''INSERT INTO apply_char (offer_id, title_id) VALUES (?, ?)''', (oid, i))
      else:
        cur.execute('''SELECT id FROM apply_title WHERE title = ?;''', (t,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO apply_title (title) VALUES (?);''', (t,))
          cur.execute('''SELECT id FROM apply_title WHERE title = ?;''', (t,))
          r = cur.fetchone()
        i = r['id']
        cur.execute('''INSERT INTO apply_detail (offer_id, title_id, comment) VALUES (?, ?, ?)''', (oid, i, offer['apply'][t]))

    for t in offer['company']:
      if t == '関連業界':
        for tt in offer['company'][t]:
          cur.execute('''SELECT id FROM apply_relation_title WHERE title = ?;''', (tt,))
          r = cur.fetchone()
          if r is None:
            cur.execute('''INSERT INTO apply_relation_title (title) VALUES (?);''', (tt,))
            cur.execute('''SELECT id FROM apply_relation_title WHERE title = ?;''', (tt,))
            r = cur.fetchone()
          i = r['id']
          cur.execute('''INSERT INTO apply_relation (offer_id, title_id) VALUES (?, ?)''', (oid, i))
      else:
        cur.execute('''SELECT id FROM apply_title WHERE title = ?;''', (t,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO apply_title (title) VALUES (?);''', (t,))
          cur.execute('''SELECT id FROM apply_title WHERE title = ?;''', (t,))
          r = cur.fetchone()
        i = r['id']
        cur.execute('''INSERT INTO apply_company (offer_id, title_id, comment) VALUES (?, ?, ?)''', (oid, i, offer['company'][t]))
      
    con.commit()
    
    
def login(session):
  req = session.get(URL)
  if req.status_code != 200:
    return None
  root = pq(req.text.encode('utf-8'))
  seacret_key = root('form#new_user.new_user div input').attr('value')
  d = {
    'authenticity_token': seacret_key,
    'user[email]': 'asproject.poem@gmail.com',
    'user[password]': 'attouteki',
    'commit': 'ログイン'
  }
  req = session.post(URL_signin, data=d)

def logout(session):
  req = session.get(URL_signout)
  
def getURLs(session, page, cat):
  params = {
    'type': 'recent',
    'occupations[]': cat,
    'hiring_types[]': 'mid_career',
    'page': page
  }
  req = session.get(URL_project, params=params)
  root = pq(req.text.encode('utf-8'))

  nf = root('div.projects-not-found p')
  if nf.text() != '':
    return None

  ret = []
  for comp in root('article.projects-index-single'):
    ret.append(comp.attrib['data-project-id'])

  if len(ret) == 0:
    ret = None
  return ret

def parse_person(project, person):
  url = 'https://www.wantedly.com/projects/{}/staffings/{}'.format(project, person)
  r = requests.get(url)
  root = pq(r.text.encode('utf-8'))
  return root('section.user-introduction-section.user-profile-section p').text()
  
def parse_page(project, root):
  job = {}
  offer = {}
  job['kind'] = root('span.icon-job-type').text()
  job['position'] = root('div.breadcrumbs span span span a span').text()
  if job['position'] == '':
    job['position'] = None
  offer['id'] = project
  offer['title'] = root('h1.project-title').text()
  offer['company'] = root('a.wt-company').text()
  offer['company_id'] = root('a.wt-company').attr['href'].split('/')[2:][0]

  interviews = []

  for c in root('ul.members.cf li').items():
    m = _re_user.search(c('a').attr['href'])
    if m is not None:
      intr = parse_person(m.group('projects'), m.group('user'))
      if len(intr) != 0:
        interviews.append(intr)
  
  details = {}
  for c in root('div.column-main-inner div.js-descriptions section').items():
    title = c('h3').text()
    body = c('div.section-body p').text()
    if title == '' or body == '':
      continue
    details[title] = body

  header = ""
  bosyu = {}
  kaisya = {}
  for tr in root('table.wanted-info tr').items():
    h = tr('th').text()
    if h != "":
      header = h
      continue
    if header == '募集情報':
      for i, h in enumerate(tr('td').items()):
        if i == 0:
          k = h.text()
        else:
          v = h.text()
      if k == '募集の特徴':
        t = v.split('/')
        v = []
        for vv in t:
          v.append(vv.strip())
      bosyu[k] = v
    elif header == '会社情報':
      for i, h in enumerate(tr('td').items()):
        if i == 0:
          k = h.text()
        else:
          v = h.text().replace('\n', '')
      if k == '関連業界':
        t = v.split(' /')
        v = []
        for vv in t:
          v.append(vv.strip())
      kaisya[k] = v
    elif header == 'もっと知りたいリクエスト':
      pass
    else:
      print(header)
      raise('Unknown column')
  return {'job':job, 'offer': offer, 'details': details, 'interview': interviews, 'apply': bosyu, 'company': kaisya}
  
def crawl_main(db):
  s = requests.session()
  login(s)
  page = 1
  while True:
    print(page)
    url_list = getURLs(s, page, ['engineer', 'web_engineer', 'mobile_engineer', 'infra_engineer', 'others_engineer', 'designer', 'ui_designer', 'graphic_designer', 'others_designer', 'director', 'corporate_staff', 'sales', 'marketing', 'writer', 'others'])
    if url_list is None:
      break
    for p in url_list:
      print(p)
      url = URL_base.format(p)
      r = requests.get(url)
      offer = parse_page(p, pq(r.text.encode('utf-8')))
      save_database(db, offer)
      time.sleep(1)
    page += 1
  logout(s)
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Crawler')
  parser.add_argument('db', metavar='DB', type=str, help='DataBase Name')

  args = parser.parse_args()

  setup_database(args.db)
  crawl_main(args.db)
