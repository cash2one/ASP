#!/usr/bin/env python3
import subprocess
import logging
import os
import datetime

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
  # Pathの決定
  home = os.environ.get('ASP_HOME', '/home/asp')
  now = datetime.datetime.utcnow()

  if os.path.isdir(home + '/db/{year:04d}'.format(year=now.year)) is False:
    os.makedirs(home + '/db/{year:04d}'.format(year=now.year))
    
  db = home + '/db/{year:04d}/{year:04d}_{week:02d}_green.sqlite3'.format(year=now.year, week=now.isocalendar()[1])

  if os.path.exists(db):
    os.unlink(db)

  crawler = home + '/crawler/green.py'
  extractor = home + '/keyword/green.py'
  ranker = home + '/ranking/green.py'
  
  # Crawlerの起動
  subprocess.check_call(['/usr/bin/env', 'python3', crawler, db])

  # Extractorの起動
  subprocess.check_call(['/usr/bin/env', 'python3', extractor, db])

  # Rankerの起動
  subprocess.check_call(['/usr/bin/env', 'python3', ranker, db])
