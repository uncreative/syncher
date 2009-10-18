import os
import logging
import undo
import shutil
import settings

class SyncherException(Exception): pass




def dryfunc(ldry, func, *kw):
    if ldry:
        logging.info("dry calling %s %s" % (func.__name__, kw))
    else:
        return func(*kw)
        

def move(src, dst):
    logging.info("moving %s to %s", src, dst)    
    dryfunc(settings.dry, shutil.move, src, dst)  
    undo.push(move, dst, src)

def symlink (src, dst):
    logging.info("creating symlink from %s to %s", src, dst)
    dryfunc(settings.dry, os.symlink, src, dst)
    undo.push(removesymlink, dst)

def removesymlink(dst):
    try:
        if os.path.islink(dst):
            logging.info("removing symlink %s ", dst)
            oldsrc = os.readlink(dst)
            dryfunc(settings.dry, os.unlink, dst)
            undo.push(symlink, oldsrc, dst)
        else:
            raise SyncherException("%s is not a symbolic link" % dst)
    except Exception as e:
        logging.warn("Failed to remove symlink %s because %s" % (dst, e))
    

def makedirs(name, mode=0777):
    logging.info("making directories: %s", name)
    if not settings.dry:
        try:
            created = makedirshelper(name, mode)
            undo.push(os.removedirs, created)
            return created
        except OSError, err:
            print repr(err)
            if err.errno == 17: pass
            else: raise
    
    

def makedirshelper(name, mode=0777):
    """makedirs(path [, mode=0777])

    Super-mkdir; create a leaf directory and all intermediate ones.
    Works like mkdir, except that any intermediate path segment (not
    just the rightmost) will be created if it does not exist.  This is
    recursive.
    
    Returns the first dir it had to create
    """
    made = None
    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not os.path.exists(head):
        try:
            made = makedirs(head, mode)
        except OSError, e:
            # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        if tail == os.curdir:           # xxx/newdir/. exists if xxx/newdir exists
            return None
    os.mkdir(name, mode)
    if made: return made
    return name
    