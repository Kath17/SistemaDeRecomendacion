#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys

con = None

try:
    con = lite.connect('similitudes.db')

    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')

    data = cur.fetchone()[0]

    print "SQLite version: {}".format(data)

except lite.Error, e:

    print "Error {}:".format(e.args[0])
    sys.exit(1)

finally:

    if con:
        con.close()
