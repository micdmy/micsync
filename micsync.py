# /usr/bin/python

import sys
import getopt
import json
import os.path
import subprocess
from copy import copy


def userSelect(numElem):
    while True:
        userInput = input('[0-' + str(numElem - 1) + ']')
        if userInput.isnumeric() and int(userInput) in list(range(0, numElem)):
            return int(userInput)
        elif userInput.isalpha() and userInput in 'Qq':
            return


def userChoose(msg, trueResponse, falseResponse):
    while True:
        userInput = input(msg + "[" + trueResponse + "/" + falseResponse + "]")
        if userInput:
            if userInput.upper() == trueResponse.upper():
                return True
            elif userInput.upper() == falseResponse.upper():
                return False


def userSelectLocation(location, locationName):
    if not location:
        return
    if len(location) == 1:
        return location[0]
    printInNewline('Choose ' + locationName +
                   ' location (Q to cancel and exit):')
    for i, loc in enumerate(location):
        printInfo('[' + str(i) + '] ' + loc)
    num = userSelect(len(location))
    if num is None:
        return
    printInfo("SELECTED: " + str(location[num]))
    return location[num]


def getAccesiblePaths(paths):
    return [p for p in paths if os.path.exists(p)]


def isAccesiblePath(path):
    return os.path.exists(path)


def prependRoot(root, paths):
    return [os.path.join(root, p) for p in paths]


def makeRelative(root, paths):
    return [os.path.relpath(p, root) for p in paths]


def normalizeList(paths):
    return [os.path.realpath(os.path.abspath(p)) for p in paths]


def normalize(path):
    return os.path.realpath(os.path.abspath(path))


def getParentDir(path):
    return os.path.dirname(path)


def appendSlash(path):
    if path.strip()[-1] != '/':
        return path + '/'
    return path


def removeSlash(path):
    woutWhite = path.strip()
    if path and woutWhite[-1] == '/' and len(woutWhite) != "/":
        return path[:-1]
    return path


def isDir(path):
    return os.path.isdir(path)


def cutLastEndline(string):
    if string and string[-1] == '\n':
        string = string[:-1]
    return string


def printError(msg):
    print('micsync.py: Error: ' + str(msg))


def printInfo(msg):
    print(str(msg))


def printInNewline(msg):
    print('\n' + str(msg))


def printIndent(msg):
    print('    ' + str(msg))


class Rsync:
    NO_OPTIONS = []
    DELETE = ["--delete"]
    NO_MODIFY = ["--ignore-existing"]
    TREE = ["--include='*/'"] + ["--exclude='*'"]

    @classmethod
    def _pathsForRsync(cls, srcsLst, dst):
        return srcsLst + [dst]

    @classmethod
    def _removeTouchedDirsFromOutput(cls, outpLines, dst):
        wholePaths = prependRoot(dst, outpLines)
        return [oL for i, oL in enumerate(outpLines) if not isDir(wholePaths[i])]

    @classmethod
    def _removeCreatedDirsFromOutput(cls, outpLines):
        return [oL for oL in outpLines if not oL.startswith("created directory ")]

    @classmethod
    def _run(cls, options, suspendTouchedDirs, suspendCreatedDirs, dst):
        command = ["rsync"] + options
        output = subprocess.run(
            args=command, stdout=subprocess.PIPE, text=True).stdout
        outpLines = output.split("\n",)
        if outpLines and outpLines[0] == "sending incremental file list":
            outpLines = outpLines[1:]
            if outpLines and outpLines[-1] == "":
                del outpLines[-1]
            if suspendCreatedDirs:
                outpLines = Rsync._removeCreatedDirsFromOutput(outpLines)
            if suspendTouchedDirs:
                outpLines = Rsync._removeTouchedDirsFromOutput(outpLines, dst)
        else:
            printError(
                "Something went wrong with rsync call. Maybe it's api has changed? Please inform the author.")
            return
        return outpLines

    @classmethod
    def shallModifyExisting(cls, srcsLst, dst, suspendPrintDirs):
        outpLines = Rsync._run(["-n", "-a", "-h", "-P", "--existing"] + Rsync._pathsForRsync(
            srcsLst, dst), suspendPrintDirs, suspendPrintDirs, dst)
        if outpLines:
            printInNewline("THIS FILES WILL BE MODIFIED in \"" + dst + "\":")
            for oL in outpLines:
                printIndent(oL)
            return userChoose("MODIFY FILES LISTED ABOVE (OTHER WILL BE COPIED ANYWAY)? ", "Modify", "No")
        else:
            printInNewline("NO FILES TO MODIFY in \"" + dst + "\"")

    @classmethod
    def shallDeleteInDst(cls, srcsLst, dst, suspendPrintDirs):
        outpLines = Rsync._run(["-n", "-a", "-h", "-P", "--delete", "--ignore-existing",
                                "--existing"] + Rsync._pathsForRsync(srcsLst, dst), suspendPrintDirs, True, dst)
        if outpLines:
            printInNewline("THIS FILES WILL BE DELETED in \"" + dst + "\":")
            for oL in outpLines:
                printIndent(oL)
            return userChoose("DELETE FILES LISTED ABOVE (OTHER WILL BE COPIED ANYWAY)? ", "Delete", "No")

    @classmethod
    def sync(cls, srcsLst, dst, options, verbose):
        if verbose:
            printInNewline("COPYING:")
            for s in srcsLst:
                printIndent(s)
            printInfo("TO:")
            printIndent(dst)
        command = ["rsync", "-a", "-v", "-h", "-P"] + \
            options + Rsync._pathsForRsync(srcsLst, dst)
        if verbose:
            if not userChoose("DO YOU WANT TO EXECUTE COMMAND:\n" + str(command) + "\n", "yes", "no"):
                return
        result = subprocess.run(
            args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = result.stdout.split("\n",)
        printNoSrc = False
        printHintTreeMode = False
        for outp in output:
            printIndent(outp)
            if "failed: No such file or directory" in outp:
                if "rsync: link_stat" in outp or "rsync: change_dir" in outp:
                    printNoSrc = True
                if "rsync: mkdir" in outp:
                    printHintTreeMode = True
        if printNoSrc:
            printInfo("NO SOURCE DIRECTORY, rsync COMMAND FAILED!")
        if printHintTreeMode:
            printInfo("NO DESTINATION DIRECTORY, rsync COMMAND FAILED!")
            printIndent("TRY TO RUN WITH --tree OPTION FIRST!")


class Flags:
    def __init__(self, optionsString):
        self.suspendPrintDirs = 's' in optionsString
        self.askForModified = 'm' not in optionsString
        self.allowDeleting = 'd' in optionsString
        self.dontAskForDeleted = 'D' in optionsString
        self.verbose = 'v' in optionsString

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
        self.applicable = []
        self.dsts = []
        self.srcs = []

    def updateFlags(self):
        self.flags = Flags(self.options)

    def loadAndCheck(self, applicable):
        self.applicable = applicable
        self.applicable['backup'] = getAccesiblePaths(
            self.applicable['backup'])
        self.applicable['work'] = getAccesiblePaths(self.applicable['work'])
        if self.applicable['fBackup']:
            self.applicable['pathsOrigin'] = getAccesiblePaths(
                self.applicable['fBackup'])[0]
        else:
            self.applicable['pathsOrigin'] = getAccesiblePaths(
                self.applicable['fWork'])[0]
        if self.applicable['backup'] and self.applicable['work'] and self.applicable['pathsOrigin']:
            return True
        else:
            return False

    def calculateSrcsAndDsts(self, paths, rootPath):
        relPaths = makeRelative(self.applicable['pathsOrigin'], paths)
        self.srcs = prependRoot(self.applicable['srcLocation'], relPaths)
        self.srcs = normalizeList(self.srcs)
        if self.srcs[0] == self.applicable['srcLocation']:
            relRootPath = '.'
            self.srcs[0] = appendSlash(self.srcs[0])
        else:
            relRootPath = makeRelative(
                self.applicable['pathsOrigin'], [rootPath])
        for dstLoc in self.applicable['dstLocations']:
            dst = prependRoot(dstLoc, relRootPath)[0]
            dst = appendSlash(normalize(dst))
            self.dsts.append(dst)
        tempDsts = []
        for dL in self.dsts:
            parent = getParentDir(removeSlash(dL))
            if isAccesiblePath(parent):
                tempDsts.append(dL)
            else:
                printInfo("COPYING TO \"" + str(dL) + "\" NOT POSSIBLE")
                printIndent("directory \"" + str(parent) +
                            "\" doesn't exist or is unaccessible!")
                printIndent("TRY TO RUN WITH --tree OPTION FIRST!")
        self.dsts = tempDsts
        if not self.dsts:
            return
        tempSrcs = []
        for sL in self.srcs:
            if isAccesiblePath(sL):
                tempSrcs.append(sL)
            else:
                printInfo("SOURCE \"" + str(sL) +
                          "\" doesn't exist or is unaccessible!")
                printIndent("COPYING THIS SOURCE WILL BE ABORTED!")
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
        if self.applicable['fBackup']:
            self.applicable['srcLocation'] = userSelectLocation(
                self.applicable['work'], 'WORK')
        else:
            self.applicable['srcLocation'] = self.applicable['fWork'][0]
        if not self.applicable['srcLocation']:
            return
        self.applicable['dstLocations'] = self.applicable['backup']
        return True


class WorkMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable['fBackup']:
            self.applicable['dstLocations'] = [
                userSelectLocation(self.applicable['work'], 'WORK')]
            self.applicable['srcLocation'] = self.applicable['fBackup'][0]
        else:
            self.applicable['dstLocations'] = [self.applicable['fWork'][0]]
            self.applicable['srcLocation'] = userSelectLocation(
                self.applicable['backup'], 'BACKUP')
        if self.applicable['dstLocations'][0] and self.applicable['srcLocation']:
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
        if len(self.applicable['backup']) < 2:
            printInfo(
                "Bad usage. There must be at least two BACKUP locations defined for this configuration!")
            return
        self.applicable['srcLocation'] = userSelectLocation(
            self.applicable['backup'], 'SOURCE BACKUP')
        if not self.applicable['srcLocation']:
            return
        remaining = [bckp for bckp in self.applicable['backup']
                     if bckp != self.applicable['srcLocation']]
        self.applicable['dstLocations'] = []
        onlyOneRemainingInitially = len(remaining) == 1
        while True:
            location = userSelectLocation(remaining, 'DESTINATION BACKUP')
            if not location:
                return
            self.applicable['dstLocations'].append(location)
            remaining = [rem for rem in remaining if rem !=
                         self.applicable['dstLocations'][-1]]
            if len(remaining) < 1:
                break
            else:
                if len(remaining) == 1 and not onlyOneRemainingInitially:
                    if userChoose("Do you want to add this DESTINATION BACKUP location too?\n" + remaining[0] + "\n", "Y", "N"):

                        self.applicable['dstLocations'].append(remaining[0])
                    break
                elif not userChoose("Do you want to add more DESTINATION BACKUP locations? ", "Y", "N"):
                    break
        return True


modes = [BackupMode('backup', 'msv'),
         WorkMode('work', 'mdDsv'),
         TransferMode('transfer', 'mdDsv'),
         TreeMode('tree', 'v')]


def configsEqual(configs):
    if not configs:
        return True
    c = configs[0]
    for config in configs:
        if c != config:
            return False
    return True


def xor(a, b):
    a = bool(a)
    b = bool(b)
    return (a and not b) or (not a and b)


def printValidSyntaxInfo(programName):
    printError('Valid syntax is:')
    for mode in modes:
        optString = ''
        for char in mode.options:
            optString += ' [-' + char + ']'
        printIndent(programName + ' --' + mode.name + optString + ' path...')


def parseInputArguments(arguments):
    for mode in modes:
        try:
            opts, args = getopt.getopt(
                arguments[1:], mode.options, [mode.name])
            opts = [opt[0] for opt in opts]
            if ("--" + mode.name) in opts:
                retMode = mode
                retMode.options = [x[1] for x in opts if (len(x) == 2
                                                          and x[0] == '-'
                                                          and x[1] in mode.options)]
                retMode.updateFlags()
                paths = normalizeList(args)
                if not paths:
                    printValidSyntaxInfo(arguments[0])
                    return None, None, None
                for path in paths:
                    if not os.path.exists(path):
                        printError('Invalid path: ' + path)
                        return None, None, None
                rootPath = getParentDir(paths[0])
                for path in paths:
                    if rootPath != getParentDir(path):
                        printError('Given paths must be in the same location')
                        return None, None, None
                return retMode, paths, rootPath
        except getopt.GetoptError:
            pass
    printValidSyntaxInfo(arguments[0])
    return None, None, None


def readConfigurations(configFileName):
    with open(configFileName, 'r') as configFile:
        try:
            configuration = json.load(configFile)
        except json.JSONDecodeError as e:
            printError("Invalid JSON config file: " + configFileName + ":")
            printIndent("Line: " + str(e.lineno) + ", Column: " +
                        str(e.colno) + ", Msg: " + e.msg)
            return None
        return configuration['configs']


def isSubpath(basepath, subpath):
    return basepath == (os.path.commonpath([basepath, subpath]))


def verifyConfigurations(configs, configFileName):
    if not configs:
        return
    for i, config in enumerate(configs):
        if 'name' not in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config nr ' + str(i) + ' has no field \"name\".')
            return
        elif 'work' not in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config \"' + str(i) + '\" has no field \"work\".')
            return
        elif 'backup' not in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config \"' + str(i) + '\" has no field \"backup\".')
            return
        config['backup'] = normalizeList(config['backup'])
        config['work'] = normalizeList(config['work'])
        for k, w1 in enumerate(config['work']):
            for l, w2 in enumerate(config['work']):
                if k != l and isSubpath(w1, w2):
                    printError('Bad work paths in config \"' +
                               config['name'] + '\"')
                    printIndent(
                        'Paths in work cannot be its subpaths or identical.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, b2 in enumerate(config['backup']):
                if k != l and isSubpath(b1, b2):
                    printError('Bad backup paths in config \"' +
                               config['name'] + '\"')
                    printIndent(
                        'Paths in backup cannot be its subpaths or identical.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, w2 in enumerate(config['work']):
                if k != l and isSubpath(b1, w2):
                    printError(
                        'Bad backup or work paths in config \"' + config['name'] + '\"')
                    printIndent(
                        'Paths in backup and work cannot be its subpaths or identical.')
                    return
    return configs


def filterConfig(config, path):
    config['fWork'] = []
    config['fBackup'] = []
    config['fWork'] = [wPath for wPath in config['work']
                       if isSubpath(wPath, path)]
    config['fBackup'] = [
        bPath for bPath in config['backup'] if isSubpath(bPath, path)]
    return config


def userSelectConfig(configs):
    if not configs:
        return
    if len(configs) == 1:
        return configs[0]
    print('Many configs applicable, select one (Q to cancel and exit):')
    for configNumber, config in enumerate(configs):
        if config['fWork']:
            print('[' + str(configNumber) + '] in WORK of ' +
                  config['name'] + ': ')
        if config['fBackup']:
            print('[' + str(configNumber) + '] in BACKUP of ' +
                  config['name'] + ': ')
    num = userSelect(len(configs))
    if num is None:
        return
    return configs[num]


def filterApplicableConfigs(configs, paths):
    applicableConfigs = []
    for config in configs:
        pathsConfig = [filterConfig(copy(config), path) for path in paths]
        if [True for pConfig in pathsConfig if (not pConfig['fBackup'] and not pConfig['fWork'])]:
            # At least one path not in BACKUP and not in WORK
            continue
        if not configsEqual(pathsConfig):
            printError('In config: ' + config['name'] + ':')
            printIndent(
                'All given paths should be in the same WORK xor BACKUP')
            return
        elif pathsConfig:
            pC = pathsConfig[0]
            if pC['fWork'] and pC['fBackup']:
                printError('In config: ' + config['name'] + ':')
                printIndent('Given paths cannot be both in WORK and BACKUP.')
                return
            elif xor(pC['fWork'], pC['fBackup']):
                applicableConfigs.append(pC)
    if not applicableConfigs:
        printError('None of given paths is in WORK or BACKUP')
    return applicableConfigs


def main(argv):
    mode, paths, rootPath = parseInputArguments(argv)
    if not mode or not paths or not rootPath:
        return -1
    configFileName = './.micsync.json'
    configs = readConfigurations(configFileName)
    configs = verifyConfigurations(configs, configFileName)
    if not configs:
        return -1
    applicables = filterApplicableConfigs(configs, paths)
    if not applicables:
        return -1
    applicable = userSelectConfig(applicables)
    if not applicable:
        return -1
    if not mode.loadAndCheck(applicable):
        return -1
    if not mode.calculateSrcsAndDsts(paths, rootPath):
        return -1
    mode.perform()


if __name__ == "__main__":
    main(sys.argv)
