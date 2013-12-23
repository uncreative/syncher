import os
import logging
import undo
import shutil
import settings


class SyncherException(Exception):
    pass


def dryfunc(ldry, func, *kw):
    if ldry:
        logging.info("dry calling %s %s" % (func.__name__, kw))
    else:
        return func(*kw)


def move(src, dst):
    logging.info("moving %s to %s", src, dst)
    dryfunc(settings.dry, shutil.move, src, dst)
    undo.push(move, dst, src)


def symlink(src, dst):
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

def removedir(path):
    try:
        logging.info("removing dir %s ", path)
        mode = oct(os.stat(path).st_mode & 0777)
        os.rmdir(path)
        undo.push(makedir, path, mode)
    except Exception as e:
        logging.warn("Failed to remove dir %s because %s" % (path, e))

def makedir(path, mode):
    try:
        logging.info("making dir %s ", path)
        os.mkdir(path, mode)
        undo.push(removedir, path)
    except Exception as e:
        logging.warn("Failed to make dir %s because %s" % (path, e))

def makedirs(name, mode=0777):
    logging.info("making directories: %s", name)
    if not settings.dry:
        try:
            made = None
            dirs = []
            #dir = os.path.basename(name)
            dirname, basename = os.path.split(name)
            if basename == '':  # if there was a / at the end of the pathname ie: /usr/local/bin/ as opposed to /usr/local/bin
                dirname, basename = os.path.split(dirname)

            while(basename != '' and not os.path.exists(os.path.join(dirname, basename))):
                dirs.append(os.path.join(dirname, basename))
                dirname, basename = os.path.split(dirname)

            while(len(dirs) > 0):
                makethis = dirs.pop()
                makedir(makethis, mode)

        except OSError, err:
            print repr(err)
            if err.errno == 17:
                pass  # file exists - should never happen, but ignore if it does
            else:
                raise

def deleteemptydirs(path):
    if not os.path.isdir(path):
        return
    if not os.listdir(path):
        logging.info("removing empty dir %s ", path)
        removedir(path)
        deleteemptydirs(os.path.dirname(path))
