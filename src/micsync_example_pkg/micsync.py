# /usr/bin/python

from paths import Paths, Path
from user import User
from configurations import Configurations

import sys
import getopt





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
