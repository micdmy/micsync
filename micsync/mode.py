#!/usr/bin/python
from .flags import Flags
from .user import User
from .rsync import Rsync
from .paths import Paths
from .paths import Path


class Mode:
    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.flags = Flags("")
        self.applicable = dict()
        self.dsts = []
        self.srcs = []

    def updateFlags(self):
        self.flags = Flags(self.options)

    def loadAndCheck(self, applicable):
        self.applicable = applicable
        self.applicable["backup"] = Paths.filter_accessible(
            self.applicable["backup"])
        self.applicable["work"] = Paths.filter_accessible(
                                            self.applicable["work"])
        if self.applicable["fBackup"]:
            self.applicable["pathsOrigin"] = Paths.filter_accessible(
                self.applicable["fBackup"])[0]
        else:
            self.applicable["pathsOrigin"] = Paths.filter_accessible(
                self.applicable["fWork"])[0]
        if self.applicable["backup"] and self.applicable["work"] \
                and self.applicable["pathsOrigin"]:
            return True
        else:
            return False

    def calculateSrcsAndDsts(self, paths, rootPath):
        r_paths = Paths.make_relative(self.applicable["pathsOrigin"], paths)
        self.srcs = Paths.prepend_root(self.applicable["srcLocation"], r_paths)
        self.srcs = Paths.normalize(self.srcs)
        if self.srcs[0] == self.applicable["srcLocation"]:
            relRootPath = "."
            self.srcs[0] = Path.append_slash(self.srcs[0])
        else:
            relRootPath = Paths.make_relative(
                self.applicable["pathsOrigin"], [rootPath])
        for dstLoc in self.applicable["dstLocations"]:
            dst = Paths.prepend_root(dstLoc, relRootPath)[0]
            dst = Path.append_slash(Path.normalize(dst))
            self.dsts.append(dst)
        tempDsts = []
        for dL in self.dsts:
            parent = Path.parent_dir(Path.remove_slash(dL))
            if Path.is_accessible(parent):
                tempDsts.append(dL)
            else:
                User.print_info("COPYING TO \"" + str(dL) + "\" NOT POSSIBLE")
                User.print_indent("directory \"" + str(parent) +
                                  "\" doesn't exist or is unaccessible!")
                User.print_indent("TRY TO RUN WITH --tree OPTION FIRST!")
        self.dsts = tempDsts
        if not self.dsts:
            return
        tempSrcs = []
        for sL in self.srcs:
            if Path.is_accessible(sL):
                tempSrcs.append(sL)
            else:
                User.print_info("SOURCE \"" + str(sL) +
                                "\" doesn't exist or is unaccessible!")
                User.print_indent("COPYING THIS SOURCE WILL BE ABORTED!")
                del sL
        self.srcs = tempSrcs
        if not self.srcs:
            return
        return True

    def perform(self):
        for dst in self.dsts:
            Rsync.sync(self.srcs, dst, self.flags.getRsyncOptions(
                dst, self.srcs), self.flags.verbose)
