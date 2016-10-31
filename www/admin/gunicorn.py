# -*- coding: utf-8 -*-

bind = 'unix:/home/asp/www/admin/tmp/admin.sock'
backlog = 2048

workers = 1
worker_class = 'sync'
worker_connections = 1000
max_request = 5000
timeout = 60
keepalive = 2

debug = False
spew = False

preload_app = True
dameon = False
pidfile = '/home/asp/www/admin/tmp/admin.pid'
user = 'asp'
group = 'asp'

logfile = '/home/asp/www/log/admin.log'
loglevel = 'info'
logconf = None

proc_name = 'admin'
