#!/usr/bin/env python
# encoding: utf-8
"""
symlinkrepos.py

Created by uncreative on 2009-09-06.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys, os, shutil
import logging
from optparse import OptionParser
#from util import dryfunc, SyncherException
import settings
import undo
import util

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"
SYNCHER_DB_FILENAME = "syncher.db"
#/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/twisted/internet/_sslverify.py:5: DeprecationWarning: the md5 module is deprecated; use hashlib instead
#  import itertools, md5



def makesymlinks(repospath):
    reposfilepath = os.path.abspath(repospath)
    with open(os.path.join(repospath, SYNCHER_DB_FILENAME)) as db:
        try:
            for line in db:
                line = line.strip()
                if not os.path.islink(line):
                    logging.info("creating symlink from %s to %s", reposfilepath + line, line)
                    if not options.dry:
                        if os.path.exists(line):
                            acl = None
                            if options.ignoreacl:
                                acl = removeacl(line)
                            util.move(line, line+".beforesyncher")#repospathtoputnewfilein)
                            if acl is not None:
                                accesscontrollist.setacl(line, acl)
                        elif not os.path.exists(os.path.dirname(line)):
                            created = util.makedirs(os.path.dirname(line))
                        util.symlink(reposfilepath + line, line)
                else:
                    if not os.path.realpath(line) == reposfilepath + line:
                        logging.warn("%s is already a symbolic link to %s not %s. it will not be followed and linked properly to repository" % (line, os.path.realpath(line), reposfilepath + line))
        except Exception as e:
            logging.warn("ROLLING BACK because of %s" % e)
            undo.rollback()
            raise

def main(argv=None):
    global options
    loglevel=logging.DEBUG #logging.WARNING
    if argv is None:
        argv = sys.argv[1:]

	options, args = settings.readoptions(argv, False)
	makesymlinks(options.repository)


if __name__ == "__main__":
	sys.exit(main())