#!/usr/bin/env python
# encoding: utf-8
"""
versionthis.py

Created by uncreative on 2009-09-06.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys, os
import logging
from externalprocess import getCommandOut, getPipedCommandOut
from util import dryfunc, SyncherException
import util
import subversion
import accesscontrollist
import syncdb
import undo
import settings


"""
# copy permissions
chown $(stat -f%u:%g "$srcdir") "$dstdir" # Copy owner and group
chmod $(stat -f%Mp%Lp "$srcdir") "$dstdir" # Copy the mode bits
(ls -lde "$srcdir"  | tail +2 | sed 's/^ [0-9]*: //'; echo) | chmod -E  "$dstdir" # Copy the ACL
"""


# ls -lde Desktop/ | tail +2 | sed 's/^ [0-9]*: //'; echo


def versionthis(filetoversion):
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
        
        created = util.makedirs(repospathtoputnewfilein)
    
        acl = None
        if options.ignoreacl:
            acl = removeacl(filetoversion)
        
        util.move(filetoversionpath, repospathofversionedfile)#repospathtoputnewfilein)

        if acl is not None:
            accesscontrollist.setacl(repospathofversionedfile, acl)
    
        util.symlink(repospathofversionedfile, filetoversionpath)
    
        svnaddme = repospathofversionedfile
        if created is not None:
            svnaddme = created
        subversion.add(svnaddme)
    
        syncdb.add(filetoversionpath)

        if options.autocommit:        
            subversion.commit([svnaddme, settings.syncdbpath], "added via versionthis")
            
    except Exception as e:
        logging.warn("ROLLING BACK because of %s" % e)
        undo.rollback()
        raise



def main(argv=None):
    global options
    loglevel=logging.DEBUG #logging.WARNING
    if argv is None:
        argv = sys.argv[1:]

	options, args = settings.readoptions(argv)
	
	if not subversion.isinsvn(options.repository):
	    raise SyncherException("%s must be added to some svn repository: %s" % options.repository)
	
	for filetoversion in args:
	    versionthis(filetoversion)

if __name__ == "__main__":
	sys.exit(main())