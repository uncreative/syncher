import os

dry = False
repospath = None
SYNCHER_DB_FILENAME = "syncher.db"

def getSyncdbPath():
    return os.path.join(repospath, SYNCHER_DB_FILENAME)