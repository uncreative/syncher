import logging
import types
import os
import traceback

undo = []
isundoing = False


def prettyaction(action):
    args = ""
    if len(action) > 1:
        argsar = []
        for arg in action[1:]:
            if isinstance(arg, types.FunctionType):
                argsar.append(arg.__name__)
            else:
                str(argsar.append(arg))
        args = ",".join([str(arg) for arg in argsar])
    if len(action) > 0:
        return "%s (%s)" % (action[0].__name__, args)
    else:
        return "EMPTY ACTION - this will fail"


def pretty():
    actions = []
    for action in undo:
        actions.append(prettyaction(action))
    return os.linesep + os.linesep.join(actions) + os.linesep


def push(*kw):
    # logging.debug("pushing %s to undo" % str(kw))
    # traceback.print_stack()
    if not isundoing:
        undo.append(kw)


def pop():
    return undo.pop()


def rollback():
    global isundoing
    dothis = None
    erroredactions = []
    try:
        isundoing = True
        logging.info("undoing: %s" % pretty())
        while len(undo) > 0:
            try:
                dothis = pop()
                dothis[0](*dothis[1:])
            except Exception as e:
                # if dothis is not None:
                #     undo.append(dothis)
                logging.warn("FAILED TO UNDO %s: REMAINING%s moving on..." % (e, pretty()))
                erroredactions.append((prettyaction(dothis), e))
        logging.info("roll back complete")
    finally:
        isundoing = False
    if len(erroredactions) > 0:
        logging.info("Failed to rollback some items")
        for erroredaction in erroredactions:
            print erroredaction[0], erroredaction[1]
