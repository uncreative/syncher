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


def makesymlinks(repospath):
    global options

    reposfilepath = os.path.abspath(repospath)
    with open(os.path.join(repospath, SYNCHER_DB_FILENAME)) as db:
        try:
            for line in db:
                line = line.strip()
                if not os.path.islink(line) and accesscontrollist.hasacl(line) and not options.ignoreacl:
                    err = "filetoversion has a 'deny' in ACL permissions (ls -lde %s: %s) \n \
                    This program is currently not clever enough to check if you have permission to move/delete this file. \n \
                    To avoid this problem remove deny permissions from the access control entries \n \
                    or rerun this command with --ignoreacl" % (line, accesscontrollist.getacl(line))
                    logging.warn(err)

                elif not os.path.islink(line):
                    acl = None
                    if not options.dry:
                        logging.info("creating symlink from %s to %s", reposfilepath + line, line)
                        if os.path.exists(line):
                            if options.ignoreacl:
                                acl = accesscontrollist.removeacl(line)
                            util.move(line, line + "-beforesyncher")  # repospathtoputnewfilein)
                        elif not os.path.exists(os.path.dirname(line)):
                            util.makedirs(os.path.dirname(line))

                        util.symlink(reposfilepath + line, line)
                        if acl is not None:
                            accesscontrollist.setacl(line, acl)
                else:
                    # if not os.path.realpath(line) == reposfilepath + line:
                    if not os.path.samefile(os.path.realpath(line), reposfilepath + line):

                        logging.warn("%s is already a symbolic link to %s not %s. it will not be followed and linked properly to repository" % (line, os.path.realpath(line), reposfilepath + line))
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
    makesymlinks(options.repository)


if __name__ == "__main__":
    sys.exit(main())
