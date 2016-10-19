#!/usr/bin/env python3
#http://www.cafe-gentle.jp/challenge/tips/python_tips_001.html

import time
import datetime
import re

import requests
import lxml.html
from pyquery import PyQuery as pq
import mysql.connector

URL = 'https://www.green-japan.com'
url_base = 'https://www.green-japan.com/search/01?page={}'
_re_job = re.compile('/job/(?P<job_id>[0-9]+)')
_re_comp = re.compile('/company/(?P<comp_id>[0-9]+)?.*')

def save_database(offer):
  connect = mysql.connector.connect(user='batch', password='@dminpass', host='localhost', database='debug_green', charset='utf8')
  cur = connect.cursor(dictionary=True)

  cur.execute('''SELECT id FROM company WHERE green_id = %s; ''', (offer['company_id'],))
  r = cur.fetchone()
  if r is None:
    cur.execute('''INSERT INTO company (green_id, name, short_description) VALUES (%s, %s, %s); ''', (offer['company_id'], offer['company_name'], offer['company_desc']))
    cur.execute('''SELECT id FROM company WHERE green_id = %s; ''', (offer['company_id'],))
    r = cur.fetchone()
  else:
    cur.execute('''UPDATE company SET name = %s, short_description = %s, modified = %s WHERE green_id = %s;''', (offer['company_name'], offer['company_desc'], datetime.datetime.now(), offer['company_id']))
  comapny_id = r['id']
    
  if offer['income'] is not None:
    cur.execute('''SELECT id FROM salary WHERE description = %s; ''', (offer['income'],))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO salary (description) VALUES (%s); ''', (offer['income'],))
      cur.execute('''SELECT id FROM salary WHERE description = %s; ''', (offer['income'],))
      r = cur.fetchone()
    else:
      cur.execute('''UPDATE salary SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
    salary_id = r['id']
  else:
    salary_id = None
  
  cur.execute('''SELECT id FROM offer WHERE green_id = %s; ''', (offer['job_id'], ))
  r = cur.fetchone()
  if r is None:
    cur.execute('''INSERT INTO offer (green_id, salary_id, company_id, title) VALUES (%s, %s, %s, %s); ''', (offer['job_id'], salary_id, comapny_id, offer['title']))
    cur.execute('''SELECT id FROM offer WHERE green_id = %s; ''', (offer['job_id'],))
    r = cur.fetchone()
  else:
    cur.execute('''UPDATE offer SET salary_id = %s, company_id = %s, title = %s, modified = %s WHERE green_id = %s; ''', (salary_id, comapny_id, offer['title'], datetime.datetime.now(), offer['job_id']))
  offer_id = r['id']

  if offer['site'] is not None:
    sites = offer['site'].split('，')
    for site in sites:
      site = site.strip()
      print(site)
      cur.execute('''SELECT id FROM site WHERE description = %s; ''', (site,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO site (description) VALUES (%s); ''', (site,))
        cur.execute('''SELECT id FROM site WHERE description = %s; ''', (site,))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE site SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
      site_id = r['id']

      cur.execute('''SELECT id FROM offer_site WHERE offer_id = %s AND site_id = %s; ''', (offer_id, site_id))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO offer_site (offer_id, site_id) VALUES (%s, %s); ''', (offer_id, site_id))
        cur.execute('''SELECT id FROM offer_site WHERE offer_id = %s AND site_id = %s; ''', (offer_id, site_id))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE offer_site SET modified = %s WHERE offer_id = %s AND site_id = %s; ''', (datetime.datetime.now(), offer_id, site_id))
  
  for title in offer['details1']:
    cur.execute('''SELECT id FROM offer_detail_title WHERE description = %s; ''', (title,))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO offer_detail_title (description) VALUES (%s); ''', (title,))
      cur.execute('''SELECT id FROM offer_detail_title WHERE description = %s; ''', (title,))
      r = cur.fetchone()
    else:
      cur.execute('''UPDATE offer_detail_title SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
    title_id = r['id']

    cur.execute('''SELECT id FROM offer_detail WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
    r = cur.fetchone()
    if r is None:
      cur.execute('''INSERT INTO offer_detail (offer_id, title_id, description) VALUES (%s, %s, %s); ''', (offer_id, title_id, offer['details1'][title]))
      cur.execute('''SELECT id FROM offer_detail WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
      r = cur.fetchone()
    else:
      cur.execute('''UPDATE offer_detail SET description = %s, modified = %s WHERE offer_id = %s AND title_id = %s; ''', (offer['details1'][title], datetime.datetime.now(), offer_id, title_id))
    
  details = offer['details2']['企業・求人概要']
  for detail in details:
    for title in detail:
      cur.execute('''SELECT id FROM offer_company_title WHERE description = %s; ''', (title,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO offer_company_title (description) VALUES (%s); ''', (title,))
        cur.execute('''SELECT id FROM offer_company_title WHERE description = %s; ''', (title,))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE offer_company_title SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
      title_id = r['id']

      cur.execute('''SELECT id FROM offer_company WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO offer_company (offer_id, title_id, description) VALUES (%s, %s, %s); ''', (offer_id, title_id, detail[title]))
        cur.execute('''SELECT id FROM offer_company WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE offer_company SET description = %s, modified = %s WHERE offer_id = %s AND title_id = %s; ''', (detail[title], datetime.datetime.now(), offer_id, title_id))

  details = offer['details2']['応募条件']
  for detail in details:
    for title in detail:
      cur.execute('''SELECT id FROM apply_title WHERE description = %s; ''', (title,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO apply_title (description) VALUES (%s); ''', (title,))
        cur.execute('''SELECT id FROM apply_title WHERE description = %s; ''', (title,))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE apply_title SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
      title_id = r['id']

      cur.execute('''SELECT id FROM apply WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO apply (offer_id, title_id, description) VALUES (%s, %s, %s); ''', (offer_id, title_id, detail[title]))
        cur.execute('''SELECT id FROM apply WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE apply SET description = %s, modified = %s WHERE offer_id = %s AND title_id = %s; ''', (detail[title], datetime.datetime.now(), offer_id, title_id))

  details = offer['details2']['勤務・就業規定・その他情報']
  for detail in details:
    for title in detail:
      cur.execute('''SELECT id FROM other_title WHERE description = %s; ''', (title,))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO other_title (description) VALUES (%s); ''', (title,))
        cur.execute('''SELECT id FROM other_title WHERE description = %s; ''', (title,))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE other_title SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
      title_id = r['id']

      cur.execute('''SELECT id FROM other WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
      r = cur.fetchone()
      if r is None:
        cur.execute('''INSERT INTO other (offer_id, title_id, description) VALUES (%s, %s, %s); ''', (offer_id, title_id, detail[title]))
        cur.execute('''SELECT id FROM other WHERE offer_id = %s AND title_id = %s; ''', (offer_id, title_id))
        r = cur.fetchone()
      else:
        cur.execute('''UPDATE other SET description = %s, modified = %s WHERE offer_id = %s AND title_id = %s; ''', (detail[title], datetime.datetime.now(), offer_id, title_id))

      if title == 'タグ':
        tags = detail[title].split(' ')
        for tag in tags:
          cur.execute('''SELECT id FROM tags WHERE tag = %s; ''', (tag,))
          r = cur.fetchone()
          if r is None:
            cur.execute('''INSERT INTO tags (tag) VALUES (%s); ''', (tag,))
            cur.execute('''SELECT id FROM tags WHERE tag = %s; ''', (tag,))
            r = cur.fetchone()
          else:
            cur.execute('''UPDATE tags SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
          tag_id = r['id']
          
          cur.execute('''SELECT id FROM offer_tag WHERE offer_id = %s AND tag_id = %s; ''', (offer_id, tag_id))
          r = cur.fetchone()
          if r is None:
            cur.execute('''INSERT INTO offer_tag (offer_id, tag_id) VALUES (%s, %s); ''', (offer_id, tag_id))
            cur.execute('''SELECT id FROM offer_tag WHERE offer_id = %s AND tag_id = %s; ''', (offer_id, tag_id))
            r = cur.fetchone()
          else:
            cur.execute('''UPDATE offer_tag SET modified = %s WHERE id = %s; ''', (datetime.datetime.now(), r['id']))
          title_id = r['id']

  print(offer_id)
  connect.commit()
  connect.close()
  
def parse_page(url):
  req = requests.get(url)
  print(url)
  if req.status_code != 200:
    return False
    
  offer = {}
  root = pq(req.text.encode('utf-8'))

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

  save_database(offer)
  time.sleep(1)

def crawl_main():
  page = 1
  while True:
    req = requests.get(url_base.format(page))
    if req.status_code != 200:
      break

    root = pq(req.text.encode('utf-8'))
    page_num = 0
    for comp in root('div.card-info__wrapper a').items():
      page_num += 1
      parse_page(URL + comp.attr['href'])
    page += 1

    if page_num == 0:
      break
    time.sleep(10)


if __name__ == '__main__':
  crawl_main()
