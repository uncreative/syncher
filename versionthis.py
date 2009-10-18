#!/usr/bin/env python
# encoding: utf-8
"""
symlinkrepos.py

Created by uncreative on 2009-09-06.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys, os
import logging
from optparse import OptionParser
from externalprocess import getCommandOut, getPipedCommandOut
from util import dryfunc, SyncherException
import util
import subversion
import accesscontrollist
import syncdb
import undo
import settings

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"

"""
# copy permissions
chown $(stat -f%u:%g "$srcdir") "$dstdir" # Copy owner and group
chmod $(stat -f%Mp%Lp "$srcdir") "$dstdir" # Copy the mode bits
(ls -lde "$srcdir"  | tail +2 | sed 's/^ [0-9]*: //'; echo) | chmod -E  "$dstdir" # Copy the ACL
"""


# ls -lde Desktop/ | tail +2 | sed 's/^ [0-9]*: //'; echo


def versionthis(repospath, filetoversion):
    try:    
        if accesscontrollist.hasacl(filetoversion) and not options.ignoreacl:
            err = "filetoversion has a 'deny' in ACL permissions (ls -lde %s: %s) \n \
            This program is currently not clever enough to check if you have permission to move/delete this file. \n \
            To avoid this problem remove deny permissions from the access control entries \n \
            or rerun this command with --ignoreacl" % (filetoversion, accesscontrollist.getacl(filetoversion))
            raise SyncherException(err)
        
        # TODO: verify that this file is not already added
        logging.info("should: check for dups")
    
        filetoversionpath = os.path.abspath(filetoversion) 
        reposfilepath = os.path.abspath(repospath) 
        repospathofversionedfile = os.path.join(repospath, filetoversionpath[1:]) # /Users/uncreative/syncher/Users/uncreative/Library/Safari/Bookmarks.plist
        repospathtoputnewfilein = os.path.join(repospath, os.path.dirname(filetoversionpath)[1:])

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
            subversion.commit([svnaddme, settings.getSyncdbPath()], "added via versionthis")
            
    except Exception as e:
        logging.warn("ROLLING BACK because of %s" % e)
        undo.rollback()
        raise


def readoptions(argv):
    usage = '''usage: %prog [options] path-to-version'''
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True, help="make lots of noise [default]")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="be vewwy quiet (I'm hunting wabbits)")
    parser.add_option("-r", "--repository", dest="repository", metavar="PATH", help="PATH of syncher repository (can be specified in SYNCHER_REPOSITORY environment variable instead)")
    parser.add_option("--dry", dest="dry", action="store_true", default=False, help="do no harm")
    parser.add_option("--ignoreacl", dest="ignoreacl", action="store_true", default=False, help="remove acl permissions before creating symlink")
    parser.add_option("--autocommit", dest="autocommit", action="store_true", default=False, help="commit file to repository after adding to subversion")
    options, args = parser.parse_args(argv)

    if options.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING

    logging.basicConfig(level=loglevel)
    
    if options.repository is None:
        options.repository = os.environ.get("SYNCHER_REPOSITORY")
    
    if options.repository is None:
        raise SyncherException("You must set an environment variable SYNCHER_REPOSITORY to path of syncher or use -r to specify the repository path")
    else:
        if not subversion.isinsvn(options.repository):
            raise SyncherException("%s must be added to some svn repository: %s" % options.repository)
        
    
    if len(args) < 1:
        raise SyncherException("You must supply one or more files to version")	
    
    settings.dry = options.dry
    settings.repospath = options.repository

    return options, args
    
def main(argv=None):
    global options
    loglevel=logging.DEBUG #logging.WARNING
    if argv is None:
        argv = sys.argv[1:]

	options, args = readoptions(argv)
	
	
		
	for filetoversion in args:
	    versionthis(options.repository, filetoversion)

if __name__ == "__main__":
	sys.exit(main())