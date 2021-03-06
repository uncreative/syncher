#!/usr/bin/env python
# encoding: utf-8
"""
desynch.py

Created by uncreative on 2009-12-31.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import logging
import settings
from util import SyncherException
import util
import accesscontrollist
import syncdb
import undo


"""
# copy permissions
chown $(stat -f%u:%g "$srcdir") "$dstdir" # Copy owner and group
chmod $(stat -f%Mp%Lp "$srcdir") "$dstdir" # Copy the mode bits
(ls -lde "$srcdir"  | tail +2 | sed 's/^ [0-9]*: //'; echo) | chmod -E  "$dstdir" # Copy the ACL
"""


# ls -lde Desktop/ | tail +2 | sed 's/^ [0-9]*: //'; echo


def unversionthis(filetoversion):
    try:
        if accesscontrollist.hasacl(filetoversion) and not options.ignoreacl:
            err = "filetoversion has a 'deny' in ACL permissions (ls -lde %s: %s) \n \
            This program is currently not clever enough to check if you have permission to move/delete this file. \n \
            To avoid this problem remove deny permissions from the access control entries \n \
            or rerun this command with --ignoreacl" % (filetoversion, accesscontrollist.getacl(filetoversion))
            raise SyncherException(err)

        # TODO: verify that this file is not already added
        logging.info("should: check for dups")

        filetoversionpath, repospathofversionedfile, repospathtoputnewfilein = settings.getFileToVersionPathes(filetoversion)

        syncdb.remove(filetoversionpath)

        util.removesymlink(filetoversionpath)

        acl = None
        if options.ignoreacl:
            acl = accesscontrollist.removeacl(repospathofversionedfile)

        util.move(repospathofversionedfile, filetoversionpath)  # repospathtoputnewfilein)

        if acl is not None:
            accesscontrollist.setacl(filetoversion, acl)

        #created = util.makedirs(repospathtoputnewfilein)
    except Exception as e:
        logging.warn("ROLLING BACK because of %s" % e)
        undo.rollback()
        raise


def main(argv=None):
    global options
    loglevel=logging.DEBUG  # logging.WARNING
    if argv is None:
        argv = sys.argv[1:]

    options, args = settings.readoptions(argv)

    for filetoversion in args:
        unversionthis(filetoversion)

if __name__ == "__main__":
    sys.exit(main())




