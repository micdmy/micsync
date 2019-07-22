# /usr/bin/python

from paths import Paths, Path
from user import User
from configurations import Configurations
from backup_mode import BackupMode
from work_mode import WorkMode
from transfer_mode import TransferMode
from tree_mode import TreeMode
import sys
import getopt

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
