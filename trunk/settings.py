import os
import logging
from optparse import OptionParser

dry = False
repospath = None
reposfilepath = None
syncdbpath = None
SYNCHER_DB_FILENAME = "syncher.db"

SYNCHER_REPOSITORY = "SYNCHER_REPOSITORY"


def getFileToVersionPathes(filetoversion):
    filetoversionpath = os.path.abspath(filetoversion) 
    repospathofversionedfile = os.path.join(repospath, filetoversionpath[1:]) # /Users/uncreative/syncher/Users/uncreative/Library/Safari/Bookmarks.plist
    repospathtoputnewfilein = os.path.join(repospath, os.path.dirname(filetoversionpath)[1:])
    return filetoversionpath, repospathofversionedfile, repospathtoputnewfilein
 
def readoptions(argv):
    global dry, repospath, reposfilepath, syncdbpath
    
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


    if len(args) < 1:
        raise SyncherException("You must supply one or more files to version")	

    dry = options.dry
    repospath = options.repository
    reposfilepath = os.path.abspath(repospath) 
    syncdbpath = os.path.join(repospath, SYNCHER_DB_FILENAME)
    

    return options, args


