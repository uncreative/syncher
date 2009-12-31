import logging
from util import dryfunc, SyncherException
from externalprocess import getCommandOut, getPipedCommandOut
import undo
import settings


def isinsvn(f):
    cmd = "svn info \"%s\"" % f
    try:
        out = dryfunc(False, getPipedCommandOut, cmd)
        if out.find("not a working copy") >= 0: return False
        if out.find("Not a versioned resource") >= 0: return False
    except:
        return False
    return True

def commit(commitme, comment):
    if not isinstance(commitme, list):
        commitme = [commitme]
    commitus = ["\"%s\"" % f for f in commitme]
    cmd = "svn ci -m \"%s\" %s" % (comment, " ".join(commitus))
    out = dryfunc(settings.dry, getPipedCommandOut, cmd)
    logging.info("RESULTS of %s : %s" % (cmd, out))
    
def add(f):
    cmd = "svn add \"%s\"" % f
    out = dryfunc(settings.dry, getPipedCommandOut, cmd)
    logging.info("RESULTS of %s : %s" % (cmd, out))
    undo.push(deleteinreposonly, f)

def deleteinreposonly(f):
    cmd = "svn del --force --keep-local \"%s\"" % f
    out = dryfunc(settings.dry, getPipedCommandOut, cmd)
    logging.info("RESULTS of %s : %s" % (cmd, out))
    undo.push(add, f)
    