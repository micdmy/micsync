# /usr/bin/python

from paths import Paths, Path
from user import User
from configurations import Configurations

import sys
import getopt
import subprocess


class Rsync:
    NO_OPTIONS = []
    DELETE = ["--delete"]
    NO_MODIFY = ["--ignore-existing"]
    TREE = ["--include=*/"] + ["--exclude=*"] # sequence is important here

    @classmethod
    def _pathsForRsync(cls, srcsLst, dst):
        return srcsLst + [dst]

    @classmethod
    def _removeTouchedDirsFromOutput(cls, outpLines, dst):
        wholePaths = Paths.prepend_root(dst, outpLines)
        return [oL for i, oL in enumerate(outpLines)
                if not Path.is_dir(wholePaths[i])]

    @classmethod
    def _removeCreatedDirsFromOutput(cls, outpLines):
        return [oL for oL in outpLines
                if not oL.startswith("created directory ")]

    @classmethod
    def _run(cls, options, suspendTouchedDirs, suspendCreatedDirs, dst):
        command = ["rsync"] + options
        output = subprocess.run(
            args=command, stdout=subprocess.PIPE, text=True).stdout
        outpLines = output.split("\n", )
        if outpLines and outpLines[0] == "sending incremental file list":
            outpLines = outpLines[1:]
            if outpLines and outpLines[-1] == "":
                del outpLines[-1]
            if suspendCreatedDirs:
                outpLines = Rsync._removeCreatedDirsFromOutput(outpLines)
            if suspendTouchedDirs:
                outpLines = Rsync._removeTouchedDirsFromOutput(outpLines, dst)
        else:
            User.print_error("Something went wrong with rsync call.\
                        Maybe it's api has changed? Please inform the author.")
            return
        return outpLines

    @classmethod
    def shallModifyExisting(cls, srcsLst, dst, suspendPrintDirs):
        command = ["-n", "-a", "-h", "-P", "--existing"]
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        outpLines = Rsync._run(command, suspendPrintDirs,
                               suspendPrintDirs, dst)
        if outpLines:
            User.print_in_newline("THIS FILES WILL BE MODIFIED in \"" + dst + "\":")
            for oL in outpLines:
                User.print_indent(oL)
            question = "MODIFY FILES LISTED ABOVE\
                        (OTHER WILL BE COPIED ANYWAY)? "
            return User.decide(question, "Modify", "No")
        else:
            User.print_in_newline("NO FILES TO MODIFY in \"" + dst + "\"")

    @classmethod
    def shallDeleteInDst(cls, srcsLst, dst, suspendPrintDirs):
        command = ["-n", "-a", "-h", "-P",
                   "--delete", "--ignore-existing", "--existing"]
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        outpLines = Rsync._run(command, suspendPrintDirs, True, dst)
        if outpLines:
            User.print_in_newline("THIS FILES WILL BE DELETED in \"" + dst + "\":")
            for oL in outpLines:
                User.print_indent(oL)
            question = "DELETE FILES LISTED ABOVE\
                        (OTHER WILL BE COPIED ANYWAY)? "
            return User.decide(question, "Delete", "No")

    @classmethod
    def sync(cls, srcsLst, dst, options, verbose):
        if verbose:
            User.print_in_newline("COPYING:")
            for s in srcsLst:
                User.print_indent(s)
            User.print_info("TO:")
            User.print_indent(dst)
        command = ["rsync", "-a", "-v", "-h", "-P"]
        command = command + options
        command = command + Rsync._pathsForRsync(srcsLst, dst)
        if verbose:
            if not User.decide("DO YOU WANT TO EXECUTE COMMAND:\n"
                              + str(command) + "\n", "yes", "no"):
                return
        result = subprocess.run(args=command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        output = result.stdout.split("\n", )
        printNoSrc = False
        printHintTreeMode = False
        for outp in output:
            User.print_indent(outp)
            if "failed: No such file or directory" in outp:
                if "rsync: link_stat" in outp or "rsync: change_dir" in outp:
                    printNoSrc = True
                if "rsync: mkdir" in outp:
                    printHintTreeMode = True
        if printNoSrc:
            User.print_info("NO SOURCE DIRECTORY, rsync COMMAND FAILED!")
        if printHintTreeMode:
            User.print_info("NO DESTINATION DIRECTORY, rsync COMMAND FAILED!")
            User.print_indent("TRY TO RUN WITH --tree OPTION FIRST!")


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
        self.applicable["work"] = Paths.filter_accessible(self.applicable["work"])
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
        relPaths = Paths.make_relative(self.applicable["pathsOrigin"], paths)
        self.srcs = Paths.prepend_root(self.applicable["srcLocation"], relPaths)
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


class BackupMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable["fBackup"]:
            self.applicable["srcLocation"] = User.select_location(
                self.applicable["work"], "WORK")
        else:
            self.applicable["srcLocation"] = self.applicable["fWork"][0]
        if not self.applicable["srcLocation"]:
            return
        self.applicable["dstLocations"] = self.applicable["backup"]
        return True


class WorkMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable["fBackup"]:
            self.applicable["dstLocations"] = [
                User.select_location(self.applicable["work"], "WORK")]
            self.applicable["srcLocation"] = self.applicable["fBackup"][0]
        else:
            self.applicable["dstLocations"] = [self.applicable["fWork"][0]]
            self.applicable["srcLocation"] = User.select_location(
                self.applicable["backup"], "BACKUP")
        if self.applicable["dstLocations"][0] \
                and self.applicable["srcLocation"]:
            return True
        return


class TreeMode(WorkMode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def perform(self):
        for dst in self.dsts:
            options = self.flags.getRsyncOptions(dst, self.srcs) + Rsync.TREE
            Rsync.sync(self.srcs, dst, options, self.flags.verbose)


class TransferMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if len(self.applicable["backup"]) < 2:
            User.print_info("Bad usage. There must be at least two BACKUP\
                       locations defined for this configuration!")
            return
        self.applicable["srcLocation"] = User.select_location(
            self.applicable["backup"], "SOURCE BACKUP")
        if not self.applicable["srcLocation"]:
            return
        remaining = [bckp for bckp in self.applicable["backup"]
                     if bckp != self.applicable["srcLocation"]]
        self.applicable["dstLocations"] = []
        onlyOneRemainingInitially = len(remaining) == 1
        while True:
            location = User.select_location(remaining, "DESTINATION BACKUP")
            if not location:
                return
            self.applicable["dstLocations"].append(location)
            remaining = [rem for rem in remaining if rem !=
                         self.applicable["dstLocations"][-1]]
            if len(remaining) < 1:
                break
            else:
                if len(remaining) == 1 and not onlyOneRemainingInitially:
                    question = "Do you want to add this DESTINATION BACKUP\
                                location too?\n"
                    if User.decide(question + remaining[0] + "\n", "Y", "N"):
                        self.applicable["dstLocations"].append(remaining[0])
                    break
                else:
                    question = "Do you want to add more DESTINATION BACKUP\
                                locations? "
                    if not User.decide(question, "Y", "N"):
                        break
        return True


modes = [BackupMode("backup", "msv"),
         WorkMode("work", "mdDsv"),
         TransferMode("transfer", "mdDsv"),
         TreeMode("tree", "vs")]






def printValidSyntaxInfo(programName):
    User.print_error("Valid syntax is:")
    for mode in modes:
        optString = ""
        for char in mode.options:
            optString += " [-" + char + "]"
        User.print_indent(programName + " --" + mode.name + optString + " path...")


def parseInputArguments(arguments):
    for mode in modes:
        try:
            opts, args = getopt.getopt(
                arguments[1:], mode.options, [mode.name])
            opts = [opt[0] for opt in opts]
            if ("--" + mode.name) in opts:
                retMode = mode

                def is_opt_known(opt):
                    return all([len(opt) == 2,
                                opt[0] == "-", opt[1] in mode.options])

                retMode.options = [opt[1] for opt in opts if is_opt_known(opt)]
                retMode.updateFlags()
                paths = Paths.normalize(args)
                if not paths:
                    printValidSyntaxInfo(arguments[0])
                    return None, None, None
                for path in paths:
                    if not Path.is_accessible(path):
                        User.print_error("Invalid path: " + path)
                        return None, None, None
                rootPath = Path.parent_dir(paths[0])
                for path in paths:
                    if rootPath != Path.parent_dir(path):
                        User.print_error("Given paths must be in the same location")
                        return None, None, None
                return retMode, paths, rootPath
        except getopt.GetoptError:
            pass
    printValidSyntaxInfo(arguments[0])
    return None, None, None



def main(argv):
    mode, paths, rootPath = parseInputArguments(argv)
    if not mode or not paths or not rootPath:
        return -1
    config_file_name = "./.micsync.json"
    configs = Configurations.read_from_file(config_file_name)
    configs = Configurations.verify(configs, config_file_name)
    if not configs:
        return -1
    applicables = Configurations.filter_applicable(configs, paths)
    if not applicables:
        return -1
    applicable = User.select_config(applicables)
    if not applicable:
        return -1
    if not mode.loadAndCheck(applicable):
        return -1
    if not mode.calculateSrcsAndDsts(paths, rootPath):
        return -1
    mode.perform()


if __name__ == "__main__":
    main(sys.argv)
