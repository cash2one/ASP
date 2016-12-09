#!/usr/bin/env python3
import subprocess
import logging
import os
import datetime
import sqlite3
import sys

from slack_log_handler import SlackLogHandler

#
# logger の基本設定
#
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

#
# 標準出力 Handler
#
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
stream.setFormatter(formatter)

#
# Slack Handler
#
slack = SlackLogHandler(
  os.getenv('SLACK_WEB_HOOK', "https://hooks.slack.com/services/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"),
      username = 'Notifier',
      emojis = {
                logging.INFO: ':grinning:',
                logging.WARNING: ':white_frowning_face:',
                logging.ERROR: ':persevere:',
                logging.CRITICAL: ':confounded:',
            }
  )
slack.setLevel(logging.INFO)
slack.setFormatter(formatter)

#
# logger に Handler を追加
#
logger.addHandler(stream)
logger.addHandler(slack)


if __name__ == '__main__':
  logger.info('Wantedly 開始しました')  
  # Pathの決定
  home = os.environ.get('ASP_HOME', '/home/asp')
  now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)

  if os.path.isdir(home + '/db/{year:04d}'.format(year=now.year)) is False:
    os.makedirs(home + '/db/{year:04d}'.format(year=now.year))
    
  db = home + '/db/{year:04d}/{year:04d}_{week:02d}_wantedly.sqlite3'.format(year=now.year, week=now.isocalendar()[1])
  maindb = home + '/db/main.sqlite3'
  
  if os.path.exists(db):
    os.unlink(db)

  crawler = home + '/crawler/wantedly.py'
  extractor = home + '/keyword/extractor.py'
  ranker = home + '/ranking/generator.py'
  ranker_pos = home + '/ranking/generator_position.py'
  
  # Crawlerの起動
  try:
    subprocess.check_call(['/usr/bin/env', 'python3', crawler, db])
  except:
    logger.error('Wantedly Crawlerが失敗しました')
    sys.exit(1)
    
  # Extractorの起動
  try:
    subprocess.check_call(['/usr/bin/env', 'python3', extractor, db])
  except:
    logger.error('Wantedly Crawlerが失敗しました')
    sys.exit(2)
    
  # Rankerの起動
  try:
    subprocess.check_call(['/usr/bin/env', 'python3', ranker, db])
    subprocess.check_call(['/usr/bin/env', 'python3', ranker_pos, db])    
  except:
    logger.error('Wantedly Rankerが失敗しました')
    sys.exit(3)

  with sqlite3.connect(maindb) as con:
    cur = con.cursor()

    sql = '''
    INSERT INTO crawl_history (site, date, year, woy, path) VALUES ('wantedly', ?, ?, ?, ?);
    '''
    cur.execute(sql, (datetime.date(year=now.year, month=now.month, day=now.day), now.year, now.isocalendar()[1], db))

    con.commit()
  logger.info('Wantedly 終了しました')
  
