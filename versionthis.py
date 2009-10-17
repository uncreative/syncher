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
from externalprocess import getCommandOut, getPipedCommandOut

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"
SYNCHER_DB_FILENAME = "syncher.db"

"""
# copy permissions
chown $(stat -f%u:%g "$srcdir") "$dstdir" # Copy owner and group
chmod $(stat -f%Mp%Lp "$srcdir") "$dstdir" # Copy the mode bits
(ls -lde "$srcdir"  | tail +2 | sed 's/^ [0-9]*: //'; echo) | chmod -E  "$dstdir" # Copy the ACL
"""
class SyncherException(Exception): pass

# ls -lde Desktop/ | tail +2 | sed 's/^ [0-9]*: //'; echo

def dryfunc(dry, func, *kw):
    if dry:
        logging.info("dry calling %s %s" % (func.__name__, kw))
    else:
        return func(kw)

def getacl(f):
    cmd = "ls -lde %s  | tail +2 | sed 's/^ [0-9]*: //'" % f
    out = dryfunc(options.dry, getPipedCommandOut,cmd)
    logging.debug("acl: %s = %s" % (cmd, out))
    if out: out = out.strip()
    return out

def hasacl(f):
    acl = getacl(f)
    #TODO: check if acl allows user to delete/move file... - don't just check 'deny' 
    if acl and acl.find("deny") >= 0: return True
    return False

def versionthis(repospath, filetoversion):
    prevacl = None
    if hasacl(filetoversion) and not options.ignoreacl:
        err = "filetoversion has a 'deny' in ACL permissions (ls -lde %s: %s) \n \
        This program is currently not clever enough to check if you have permission to move/delete this file. \n \
        To avoid this problem remove deny permissions from the access control entries \n \
        or rerun this command with --ignoreacl" % (filetoversion, getacl(filetoversion))
        raise SyncherException(err)
        
    # ~/syncher, Safari/Bookmarks.plist
    # TODO: verify that this file is not already added
    logging.info("should: check for dups")
    
    filetoversionpath = os.path.abspath(filetoversion) # /Users/uncreative/Library/Safari/Bookmarks.plist
    reposfilepath = os.path.abspath(repospath) # /Users/uncreative/syncher
    
    # /Users/uncreative/syncher/Users/uncreative/Library/Safari/
    print os.path.dirname(filetoversionpath)
    print reposfilepath
    repospathtoputnewfilein = os.path.join(repospath, os.path.dirname(filetoversionpath)[1:])
    logging.info("making directories: %s", repospathtoputnewfilein)
    if not options.dry:
        try:
            os.makedirs(repospathtoputnewfilein)
        except OSError, err:
            print repr(err)
            if err.errno == 17: pass
            else: raise
    
    acl = None
    if options.ignoreacl:
        acl = getacl(filetoversion)
        if len(acl) > 0:
            logging.info("removing acl %s from %s" % (acl, filetoversion))
            cmd = "chmod -N %s" % filetoversion
            dryfunc(options.dry, getCommandOut, cmd)
        else:
            acl = None
        
    logging.info("moving %s to %s", filetoversionpath, repospathtoputnewfilein)
    if not options.dry:        
        shutil.move(filetoversionpath, repospathtoputnewfilein)
        

    # /Users/uncreative/Library/Safari/Bookmarks.plist , /Users/uncreative/syncher/Users/uncreative/Library/Safari/
    repospathofversionedfile = os.path.join(repospath, filetoversionpath[1:]) # /Users/uncreative/syncher/Users/uncreative/Library/Safari/Bookmarks.plist

    if acl is not None:
        logging.info("putting acl %s back to %s" % (acl, repospathofversionedfile))
        dryfunc(options.dry, getCommandOut, "echo %s | chmod -E %s" % (acl, repospathofversionedfile))
    
    
    logging.info("creating symlink from %s to %s", repospathofversionedfile, filetoversionpath)
    if not options.dry:
        os.symlink(repospathofversionedfile, filetoversionpath)
    
    cmd = "svn add %s/* --force" % options.repository    
    out = dryfunc(options.dry, getCommandOut, cmd)
    logging.info("RESULTS of %s : %s" % (cmd, out))
    
    with open(os.path.join(repospath, SYNCHER_DB_FILENAME), 'a') as db:
        if not options.dry:
            db.write(filetoversionpath + os.linesep)
        logging.info("appended %s to db", filetoversionpath)

def readoptions(argv):
    usage = '''usage: %prog [options] path-to-version'''
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True, help="make lots of noise [default]")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="be vewwy quiet (I'm hunting wabbits)")
    parser.add_option("-r", "--repository", dest="repository", metavar="PATH", help="PATH of syncher repository (can be specified in SYNCHER_REPOSITORY environment variable instead)")
    parser.add_option("--dry", dest="dry", action="store_true", default=False, help="do no harm")
    parser.add_option("--ignoreacl", dest="ignoreacl", action="store_true", default=False, help="remove acl permissions before creating symlink")
    options, args = parser.parse_args(argv)

    if options.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING

    logging.basicConfig(level=loglevel)
    
    if options.repository is None:
        options.repository = os.environ.get("SYNCHER_REPOSITORY")
    
    if options.repository is None:
        raise Exception("You must set an environment variable SYNCHER_REPOSITORY to path of syncher or use -r to specify the repository path")
    if len(args) < 1:
        raise Exception("You must supply one or more files to version")	
    
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