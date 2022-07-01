#!/usr/bin/env bash

python3 setup.py

chown www-data:www-data Intectainment/content
chown www-data:www-data Intectainment/content/database.db || true

service nginx start
uwsgi --ini uwsgi.ini