#!/usr/bin/env bash

if test -f "setup.py"; then
    python setup.py
    rm setup.py
fi

service nginx start
uwsgi --ini uwsgi.ini