import logging
from util import dryfunc, SyncherException
from externalprocess import getCommandOut, getPipedCommandOut
import settings
import undo

def getacl(f):
    cmd = "ls -lde \"%s\"  | tail +2 | sed 's/^ [0-9]*: //'" % f
    out = dryfunc(False, getPipedCommandOut,cmd)
    logging.debug("acl: %s = %s" % (cmd, out))
    if out: out = out.strip()
    return out

def hasacl(f):
    acl = getacl(f)
    #TODO: check if acl allows user to delete/move file... - don't just check 'deny' 
    if acl and acl.find("deny") >= 0: return True
    return False

def setacl(f, acl):
    oldacl = getacl(f)
    logging.info("putting acl %s on %s" % (acl, f))
    dryfunc(settings.dry, getPipedCommandOut, "echo %s | chmod -E %s" % (acl, f))    
    if len(oldacl) > 0:
        undo.push(setacl, f, oldacl)
    undo.push(removeacl, f)

def removeacl(f):
    acl = getacl(f)
    if len(acl) > 0:
        logging.info("removing acl %s from %s" % (acl, f))
        cmd = "chmod -N %s" % f
        dryfunc(settings.dry, getCommandOut, cmd)
        undo.push(setacl, f, acl)
        return acl
    