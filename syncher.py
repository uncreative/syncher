

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
from externalprocess import getCommandOut, getPipedCommandOut, dryfunc

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"
SYNCHER_DB_FILENAME = "syncher.db"
#/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/twisted/internet/_sslverify.py:5: DeprecationWarning: the md5 module is deprecated; use hashlib instead
#  import itertools, md5






def sync(repospath, comment = ""):
	reposfilepath = os.path.abspath(repospath)
	with open(os.path.join(repospath, SYNCHER_DB_FILENAME)) as db:
		for line in db:
		    logging.info("synching", reposfilepath + line, line)		    
		    if not options.dry:
		        cmd = "svn st %s | grep ^\! | gawk '{ print $2 }' | xargs svn del" % reposfilepath + line
		        out = dryfunc(options.dry, getPipedCommandOut, cmd)
			    logging.debug(out)
			    cmd = "svn ci %s -m \"sync %s\"" % (reposfilepath + line, comment)
			    out = dryfunc(options.dry, getCommandOut, cmd)
			    

def readoptions(argv):
    usage = '''usage: %prog [options] path-to-version'''
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True, help="make lots of noise [default]")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", help="be vewwy quiet (I'm hunting wabbits)")
    parser.add_option("-r", "--repository", dest="repository", metavar="PATH", help="PATH of syncher repository (can be specified in SYNCHER_REPOSITORY environment variable instead)")
    parser.add_option("--dry", dest="dry", action="store_true", default=False, help="do no harm")
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
	sync(options.repository)


if __name__ == "__main__":
	sys.exit(main())
