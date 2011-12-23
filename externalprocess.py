import logging
import tempfile
import subprocess
import os


class CommandRunError(Exception):
    pass


def getCommandOut(cmd):
    """
    cmd - command to execute

    gathers output of command (stderr and stdout) into a temp file

    returns the output of the command
    """
    logging.debug('starting %s' % cmd)

    temp = tempfile.TemporaryFile('w+t')
    try:
        p = subprocess.Popen(cmd.split(), stderr=subprocess.STDOUT, stdout=temp.fileno())
        #pid, status = os.waitpid(p.pid,0) #@UnusedVariable
        status = p.wait()
        temp.seek(0)
        out = temp.read()
        if status != 0:
            raise CommandRunError("COMMAND: %s\tFAILED: %s%s%s" % (cmd, status, os.linesep, out))
        logging.debug('finished %s' % cmd)
    finally:
        temp.close()
    return out


def getPipedCommandOut(cmd):
    """
    cmd - command to execute

    gathers output of command (stderr and stdout) into a temp file

    returns the output of the command
    """
    logging.debug('starting %s' % cmd)

    temp = tempfile.TemporaryFile('w+t')
    try:
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=temp.fileno(), shell=True)
        #pid, status = os.waitpid(p.pid,0) #@UnusedVariable
        status = p.wait()
        temp.seek(0)
        out = temp.read()
        if status != 0:
            raise CommandRunError("COMMAND: %s\tFAILED: %s%s%s" % (cmd, status, os.linesep, out))
        logging.debug('finished %s' % cmd)
    finally:
        temp.close()
    return out