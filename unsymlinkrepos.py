#!/usr/bin/env python
# encoding: utf-8
"""
symlinkrepos.py

Created by uncreative on 2009-09-06.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import logging
#from util import dryfunc, SyncherException
import settings
import undo
import util
import accesscontrollist

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"
SYNCHER_DB_FILENAME = "syncher.db"
#/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/twisted/internet/_sslverify.py:5: DeprecationWarning: the md5 module is deprecated; use hashlib instead
#  import itertools, md5


def removesymlinks(repospath):
    global options

    reposfilepath = os.path.abspath(repospath)
    with open(os.path.join(repospath, SYNCHER_DB_FILENAME)) as db:
        try:
            for line in db:
                line = line.strip()
                if not os.path.islink(line):
                    logging.warn("file is not linked to repo: %s" % (line))
                elif not os.path.samefile(os.path.realpath(line), reposfilepath + line):
                        logging.warn("%s is a symbolic link to %s not %s. it will not be removed" % (line, os.path.realpath(line), reposfilepath + line))
                elif not options.dry:
                    logging.info("deleting symlink at %s", reposfilepath + line)
                    util.removesymlink(line)
                    if os.path.exists(line + "-beforesyncher"):
                        util.move(line + "-beforesyncher", line)
                    else:
                        logging.info("no original file to restore for %s", line)

                if not options.dry and not os.path.exists(line) and options.deleteemptydirs:
                    util.deleteemptydirs(os.path.dirname(line))
        except Exception as e:
            logging.warn("ROLLING BACK because of %s" % e)
            undo.rollback()
            raise


def main(argv=None):
    global options
    loglevel = logging.DEBUG  # logging.WARNING
    if argv is None:
        argv = sys.argv[1:]

    options, args = settings.readoptions(argv, False)
    removesymlinks(options.repository)


if __name__ == "__main__":
    sys.exit(main())
