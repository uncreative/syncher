import os
import logging
from util import dryfunc, SyncherException
import util
import undo
import settings


def remove(filetoversionpath):
    with open(settings.syncdbpath, 'r') as db:
        before = db.read()
    dbwithfileremoved = before.replace(filetoversionpath + os.linesep, "")
    with open(settings.syncdbpath, 'w') as db:
        dryfunc(settings.dry, db.write, dbwithfileremoved)
        logging.info("removed %s from db", filetoversionpath)
    undo.push(add, filetoversionpath)

def add(filetoversionpath):
    with open(settings.syncdbpath, 'a') as db:
        dryfunc(settings.dry, db.write, filetoversionpath + os.linesep)
        logging.info("appended %s to db", filetoversionpath)
    undo.push(remove, filetoversionpath)
