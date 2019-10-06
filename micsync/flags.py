#!/usr/bin/python
from .rsync import Rsync


class Flags:
    def __init__(self, optionsString):
        self.suspendPrintDirs = "s" in optionsString
        self.askForModified = "m" not in optionsString
        self.allowDeleting = "d" in optionsString
        self.dontAskForDeleted = "D" in optionsString
        self.verbose = "v" in optionsString

    def getRsyncOptions(self, dst, srcs):
        if self.askForModified:
            optNoModify = Rsync.NO_OPTIONS if Rsync.shallModifyExisting(
                srcs, dst, self.suspendPrintDirs) else Rsync.NO_MODIFY
        else:
            optNoModify = Rsync.NO_OPTIONS
        if self.dontAskForDeleted:
            optDelete = Rsync.DELETE
        else:
            if self.allowDeleting:
                optDelete = Rsync.DELETE if Rsync.shallDeleteInDst(
                    srcs, dst, self.suspendPrintDirs) else Rsync.NO_OPTIONS
            else:
                optDelete = Rsync.NO_OPTIONS
        return optNoModify + optDelete

