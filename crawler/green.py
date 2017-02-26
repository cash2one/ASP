#!/usr/bin/env python3
#http://www.cafe-gentle.jp/challenge/tips/python_tips_001.html

import time
import datetime
import re
import os
import sqlite3
import argparse

import requests
import lxml.html
from pyquery import PyQuery as pq


URL = 'https://www.green-japan.com'
url_base = 'https://www.green-japan.com/search/01?page={}'
_re_job = re.compile('/job/(?P<job_id>[0-9]+)')
_re_comp = re.compile('/company/(?P<comp_id>[0-9]+)?.*')
_re_position = re.compile('(?P<pos>.*)の求人')

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
      green_id BIGINT UNSIGNED NOT NULL,
      salary_id BIGINT UNSIGNED,
      company_id BIGINT UNSIGNED NOT NULL,
      position_id BIGINT UNSIGNED NOT NULL,
      title TEXT NOT Null
    )
    '''
    cur.execute(sql)
    
    sql = '''
    CREATE TABLE salary (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) UNIQUE NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE position (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) UNIQUE NOT NULL
    )
    '''
    cur.execute(sql)
    
    sql = '''
    CREATE TABLE offer_site (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      site_id BIGINT UNSIGNED NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE site (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) UNIQUE NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE offer_detail (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id INT UNSIGNED NOT NULL,
      title_id INT UNSIGNED NOT NULL,
      description TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE offer_detail_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) UNIQUE NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE company (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      green_id INT UNSIGNED UNIQUE,
      name TEXT NOT NULL,
      short_description TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE offer_company (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      description TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE offer_company_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) NOT NULL UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      description TEXT NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE apply_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) NOT NULL UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE other (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED NOT NULL,
      title_id BIGINT UNSIGNED NOT NULL,
      description TEXT
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE other_title (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      description VARCHAR(128) NOT NULL UNIQUE
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE offer_tag (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      offer_id BIGINT UNSIGNED,
      tag_id BIGINT UNSIGNED NOT NULL
    )
    '''
    cur.execute(sql)

    sql = '''
    CREATE TABLE tags (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tag VARCHAR(128) UNIQUE NOT NULL
    )
    '''
    cur.execute(sql)
    con.commit()
  
    
def save_database(db, offer):
  with sqlite3.connect(db) as con:
    con.row_factory = dict_factory
    cur = con.cursor()
    
    cur.execute('''SELECT id FROM company WHERE green_id = ?; ''', (offer['company_id'],))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO company (green_id, name, short_description) VALUES (?, ?, ?); ''', (offer['company_id'], offer['company_name'], offer['company_desc']))
      cur.execute('''SELECT id FROM company WHERE green_id = ?; ''', (offer['company_id'],))
      r = cur.fetchone()
    else:
      cur.execute('''UPDATE company SET name = ?, short_description = ? WHERE green_id = ?;''', (offer['company_name'], offer['company_desc'], offer['company_id']))
    comapny_id = r['id']

    cur.execute('''SELECT id FROM position WHERE description = ?; ''', (offer['position'],))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO position (description) VALUES (?); ''', (offer['position'],))
      cur.execute('''SELECT id FROM position WHERE description = ?; ''', (offer['position'],))
      r = cur.fetchone()
    pos_id = r['id']
    
    if offer['income'] is not None:
      cur.execute('''SELECT id FROM salary WHERE description = ?; ''', (offer['income'],))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO salary (description) VALUES (?); ''', (offer['income'],))
        cur.execute('''SELECT id FROM salary WHERE description = ?; ''', (offer['income'],))
        r = cur.fetchone()
      salary_id = r['id']
    else:
      salary_id = None

    cur.execute('''SELECT id FROM offer WHERE green_id = ?; ''', (offer['job_id'], ))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO offer (green_id, salary_id, company_id, position_id, title) VALUES (?, ?, ?, ?, ?); ''', (offer['job_id'], salary_id, comapny_id, pos_id, offer['title']))
      cur.execute('''SELECT id FROM offer WHERE green_id = ?; ''', (offer['job_id'],))
      r = cur.fetchone()
    else:
      cur.execute('''UPDATE offer SET salary_id = ?, company_id = ?, title = ? WHERE green_id = ?; ''', (salary_id, comapny_id, offer['title'], offer['job_id']))
    offer_id = r['id']

    if offer['site'] is not None:
      sites = offer['site'].split('，')
      for site in sites:
        site = site.strip()
        cur.execute('''SELECT id FROM site WHERE description = ?; ''', (site,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO site (description) VALUES (?); ''', (site,))
          cur.execute('''SELECT id FROM site WHERE description = ?; ''', (site,))
          r = cur.fetchone()
        site_id = r['id']

        cur.execute('''SELECT id FROM offer_site WHERE offer_id = ? AND site_id = ?; ''', (offer_id, site_id))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO offer_site (offer_id, site_id) VALUES (?, ?); ''', (offer_id, site_id))
          cur.execute('''SELECT id FROM offer_site WHERE offer_id = ? AND site_id = ?; ''', (offer_id, site_id))
          r = cur.fetchone()

    for title in offer['details1']:
      cur.execute('''SELECT id FROM offer_detail_title WHERE description = ?; ''', (title,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO offer_detail_title (description) VALUES (?); ''', (title,))
        cur.execute('''SELECT id FROM offer_detail_title WHERE description = ?; ''', (title,))
        r = cur.fetchone()
      title_id = r['id']

      cur.execute('''SELECT id FROM offer_detail WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO offer_detail (offer_id, title_id, description) VALUES (?, ?, ?); ''', (offer_id, title_id, offer['details1'][title]))
        cur.execute('''SELECT id FROM offer_detail WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE offer_detail SET description = ? WHERE offer_id = ? AND title_id = ?; ''', (offer['details1'][title], offer_id, title_id))

    details = offer['details2']['企業・求人概要']
    for detail in details:
      for title in detail:
        cur.execute('''SELECT id FROM offer_company_title WHERE description = ?; ''', (title,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO offer_company_title (description) VALUES (?); ''', (title,))
          cur.execute('''SELECT id FROM offer_company_title WHERE description = ?; ''', (title,))
          r = cur.fetchone()
        title_id = r['id']

        cur.execute('''SELECT id FROM offer_company WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO offer_company (offer_id, title_id, description) VALUES (?, ?, ?); ''', (offer_id, title_id, detail[title]))
          cur.execute('''SELECT id FROM offer_company WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
          r = cur.fetchone()
        else:
          cur.execute('''UPDATE offer_company SET description = ? WHERE offer_id = ? AND title_id = ?; ''', (detail[title], offer_id, title_id))

    details = offer['details2']['応募条件']
    for detail in details:
      for title in detail:
        cur.execute('''SELECT id FROM apply_title WHERE description = ?; ''', (title,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO apply_title (description) VALUES (?); ''', (title,))
          cur.execute('''SELECT id FROM apply_title WHERE description = ?; ''', (title,))
          r = cur.fetchone()
        title_id = r['id']

        cur.execute('''SELECT id FROM apply WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO apply (offer_id, title_id, description) VALUES (?, ?, ?); ''', (offer_id, title_id, detail[title]))
          cur.execute('''SELECT id FROM apply WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
          r = cur.fetchone()
        else:
          cur.execute('''UPDATE apply SET description = ? WHERE offer_id = ? AND title_id = ?; ''', (detail[title], offer_id, title_id))

    details = offer['details2']['勤務・就業規定・その他情報']
    for detail in details:
      for title in detail:
        cur.execute('''SELECT id FROM other_title WHERE description = ?; ''', (title,))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO other_title (description) VALUES (?); ''', (title,))
          cur.execute('''SELECT id FROM other_title WHERE description = ?; ''', (title,))
          r = cur.fetchone()
        title_id = r['id']

        cur.execute('''SELECT id FROM other WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
        r = cur.fetchone()
        if r is None:
          cur.execute('''INSERT INTO other (offer_id, title_id, description) VALUES (?, ?, ?); ''', (offer_id, title_id, detail[title]))
          cur.execute('''SELECT id FROM other WHERE offer_id = ? AND title_id = ?; ''', (offer_id, title_id))
          r = cur.fetchone()
        else:
          cur.execute('''UPDATE other SET description = ? WHERE offer_id = ? AND title_id = ?; ''', (detail[title], offer_id, title_id))

        if title == 'タグ':
          tags = detail[title].split(' ')
          for tag in tags:
            cur.execute('''SELECT id FROM tags WHERE tag = ?; ''', (tag,))
            r = cur.fetchone()
            if r is None:
              cur.execute('''INSERT INTO tags (tag) VALUES (?); ''', (tag,))
              cur.execute('''SELECT id FROM tags WHERE tag = ?; ''', (tag,))
              r = cur.fetchone()
            tag_id = r['id']

            cur.execute('''SELECT id FROM offer_tag WHERE offer_id = ? AND tag_id = ?; ''', (offer_id, tag_id))
            r = cur.fetchone()
            if r is None:
              cur.execute('''INSERT INTO offer_tag (offer_id, tag_id) VALUES (?, ?); ''', (offer_id, tag_id))
              cur.execute('''SELECT id FROM offer_tag WHERE offer_id = ? AND tag_id = ?; ''', (offer_id, tag_id))
              r = cur.fetchone()

    print(offer_id, offer['job_id'])
    con.commit()
  
def parse_page(db, url, session):
  if url == 'https://www.green-japan.com/job/37473':
    return
  req = session.get(url)
  if req.status_code != 200:
    return False
    
  offer = {}
  root = pq(req.text.encode('utf-8'))

  for i, a in enumerate(root('div#content.content ul#pan li a').items()):
    if i == 2:
      _m = _re_position.search(a.text())
      offer['position'] = _m.group('pos')
  
  offer['job_id'] = _re_job.search(root('li#com_menu_job_detail a').attr['href']).group('job_id')
  offer['company_id'] = _re_comp.search(root('li#com_menu_com_detail a').attr['href']).group('comp_id')

  offer['position'] = root('div.job-offer-heading__left div.job-offer-icon').text()
  offer['title'] = root('div.job-offer-heading__left h2').text()
  company_tmp = root('div.job-offer-heading__left p').text().split('-')
  offer['company_name'] = company_tmp[0]
  offer['company_desc'] = '-'.join(company_tmp[1:])

  offer['income'] = None
  offer['site'] = None
  for li in root('ul.job-offer-meta-tags li').items():
    if li('span').attr('class') == 'icon-salary':
      offer['income'] = li.text()
    if li('span').attr('class') == 'icon-site':
      offer['site'] = li.text()

  titles = root('div.job-offer-main-content h4')
  bodies = root('div.job-offer-main-content p')

  offer_detail = {}
  for title, body in zip(titles.items(), bodies.items()):
    offer_detail[title.text()] = body.text()

  offer['details1'] = offer_detail
    
  h3s = root('h3.section-title')
  details_title = []
  for h3 in h3s:
    details_title.append(h3.text)

  tables = root('table.detail-content-table')
  details_detail = []
  for table in tables.items():
    title = []
    body = []
    for th in table('tr th').items():
      title.append(th.text())
    for td in table('tr td').items():
      body.append(td.text())

    d = []
    for t, b in zip(title, body):
      d.append({t: b})
    details_detail.append(d)
    
  details = {}
  for t, d in zip(details_title, details_detail):
    details[t] = d

  offer['details2'] = details

  save_database(db, offer)
  time.sleep(1)

def login(session):
  req = session.get('https://www.green-japan.com/login')
  if req.status_code != 200:
    return None
  root = pq(req.text.encode('utf-8'))
  utf8 = '✓'
  seacret_key = root('form#new_user.new_user input#authenticity_token').attr('value')
  for r in root('form#new_user.new_user div input'):
    if r.attrib['name'] == 'utf8':
      utf8 = r.value
    elif r.attrib['name'] == 'authenticity_token':
      seacret_key = r.value
  d = {
    'authenticity_token': seacret_key,
    'utf8': utf8,
    'user[mail]': 'asproject.poem@gmail.com',
    'user[password]': 'attouteki',
    'user[auto_login_flg]': 1,
    'commit': 'ログイン',
    'target_url': 'https://www.green-japan.com/',
  }
  req = session.post('https://www.green-japan.com/create', data=d)

def logout(session):
  req = session.get('https://www.green-japan.com/logout')
  
def crawl_main(db):
  user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'}
  s = requests.session()
  logout(s)
  login(s)
  page = 1
  while True:
    req = requests.get(url_base.format(page), headers=user_agent)
    if req.status_code != 200:
      break

    root = pq(req.text.encode('utf-8'))
    page_num = 0
    for comp in root('div.card-info__wrapper a').items():
      page_num += 1
      parse_page(db, URL + comp.attr['href'], s)
    page += 1

    if page_num == 0:
      break
    time.sleep(10)
  login(s)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Crawler')
  parser.add_argument('db', metavar='DB', type=str, help='DataBase Name')

  args = parser.parse_args()

  setup_database(args.db)
  crawl_main(args.db)
