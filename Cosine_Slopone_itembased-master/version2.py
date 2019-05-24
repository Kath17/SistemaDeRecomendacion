#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sqlite3 as lite

con = lite.connect('similitudes.db')

with con:

    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')

    data = cur.fetchone()[0]

    print "SQLite version: {}".format(data)
