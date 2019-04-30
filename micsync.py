#/usr/bin/python

import sys, getopt, json, os.path, subprocess
from copy import copy

def userSelect(numElem):
    while True:
        userInput = input('[0-' + str(numElem -1) + ']')
        if userInput.isnumeric() and int(userInput) in (0, numElem - 1):
            return int(userInput)
        elif userInput.isalpha() and userInput in 'Qq':
            return 

def userYes(msg):
    while True:
        userInput = input(msg + " [Y/N]")
        if userInput.isalpha():
            if userInput in "Yy":
                return True
            elif userInput in "Nn":
                return False

def userSelectLocation(location, locationName):
    if not location:
        return
    if len(location) == 1:
        return location[0]
    print('Choose ' + locationName + ' location (Q to cancel and exit):')
    for i, w in enumerate(location):
        print('[' + str(i) + '] ' + w)
    num = userSelect(len(location))
    if not num:
        return
    return location[num] 

def getAccesiblePaths(paths):
    return [p for p in paths if os.path.exists(p)]

def prependRoot(root, paths):
    return [os.path.join(root, p) for p in paths] 

def makeRelative(root, paths):
    return [os.path.relpath(p, root) for p in paths]

def normalizeList(paths):
    return [os.path.realpath(os.path.abspath(p)) for p in paths]

def normalize(path):
    return os.path.realpath(os.path.abspath(path))

def appendSlash(path):
    if path.strip()[-1] != '/':
        return path + '/'
    return path

def printError(msg):
    print('micsync.py: Error: ' + str(msg)) 

def printInfo(msg):
    print('micsync.py: ' + str(msg))

def printIndent(msg):
    print('    ' + str(msg))

class Rsync:
    def _pathsForRsync(srcsLst, dst):
        return "".join((" " + s) for s in srcsLst) + " " + dst
    
    def shallModifyExisting(srcsLst, dst):
        printInfo("THIS FILES WILL BE MODIFIED in \"" + dst + "\":") 
        command = "rsync -navhP --existing" + Rsync._pathsForRsync(srcsLst, dst)
        subprocess.run(command, shell=True)
        return userYes("MODIFY FILES LISTED ABOVE?")

    def backup(srcsLst, dst):
        printInfo("BACKUP to \"" + dst + "\":") 
        command = "rsync -avhP" + Rsync._pathsForRsync(srcsLst, dst)
        subprocess.run(command, shell=True)

        
class Mode:
    def __init__(self, name, options):
        self.name = name
        self.options = options
    def loadAndCheck(self, applicable):
        self.applicable = applicable
        self.applicable['backup'] = getAccesiblePaths(self.applicable['backup'])
        self.applicable['work'] = getAccesiblePaths(self.applicable['work'])
        if self.applicable['fBackup']:
            self.applicable['pathsOrigin'] = getAccesiblePaths(self.applicable['fBackup'])[0]
        else:
            self.applicable['pathsOrigin'] = getAccesiblePaths(self.applicable['fWork'])[0]
        if self.applicable['backup'] and self.applicable['work'] and self.applicable['pathsOrigin']:
            return True
        else: 
            return False

class BackupMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)
        self.dsts = []
        self.srcs = []
    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable['fBackup']:
            self.applicable['sWork'] = userSelectLocation(self.applicable('work'), 'WORK')
        else:
            self.applicable['sWork'] = self.applicable['fWork'][0]
        if not self.applicable['sWork']:
            return
        return True
    def calculateSrcsAndDsts(self, paths, rootPath):
        print('origin: ' + self.applicable['pathsOrigin'])
        relPaths = makeRelative(self.applicable['pathsOrigin'], paths)
        print('relPaths' + str(relPaths))
        self.srcs = prependRoot(self.applicable['sWork'], relPaths)
        self.srcs = normalizeList(self.srcs)
        print('root: ' + rootPath)  
        print('self.srcs: ' + str(self.srcs))
        if(self.srcs[0] == self.applicable['sWork']):
            print('KROPKA')
            relRootPath = '.'
            self.srcs[0] = appendSlash(self.srcs[0])
        else:
            relRootPath = makeRelative(self.applicable['pathsOrigin'], [rootPath])
        print('relRootPath: ' + str(relRootPath))
        for  backup in self.applicable['backup']:
            dst = prependRoot(backup, relRootPath)[0]
            dst =  appendSlash(normalize(dst))
            self.dsts.append(dst)
    def perform(self):
        print('SRCS: ' + str(self.srcs))
        print('DSTS: ' + str(self.dsts))
        for dst in self.dsts:
            if(Rsync.shallModifyExisting(self.srcs, dst)):
                Rsync.backup(self.srcs, dst)

class WorkMode:
    def __init__(self, name, options):
        super().__init__(name, options)
        self.dsts = []
        self.srcs = []
    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable['fBackup']:
            self.applicable['sWork'] = userSelectLocation(self.applicable('work'), 'WORK')
            self.applicable['sBackup'] = self.applicable['fBackup'][0]
        else:
            self.applicable['sWork'] = self.applicable['fWork'][0]
            self.applicable['sBackup'] = userSelectLocation(self.applicable['backup'], 'BACKUP')
        if self.applicable['sWork'] and self.applicable['sBackup']:
            return True
        return
    def calculateSrcsAndDsts(self, paths, rootPath):
        relPaths = makeRelative(self.applicable['pathsOrigin'], paths)
        self.srcs = prependRoot(self.applicable['sBackup'], relPaths)
        self.srcs = normalizeList(self.srcs)
        if(self.srcs[0] == self.applicable['sBackup']):
            relRootPath = '.'
            self.srcs[0] = appendSlash(self.srcs[0])
        else:
            relRootPath = makeRelative(self.applicable['pathsOrigin'], [rootPath])
        dst = prependRoot(self.applicable['sWork'], relRootPath)[0]
        dst =  appendSlash(normalize(dst))
        self.dsts[0] = dst
    def perform(self):
        print('SRCS: ' + str(self.srcs))
        print('DSTS: ' + str(self.dsts))
        if(Rsync.shallModifyExisting(self.srcs, dst)):
                Rsync.backup(self.srcs, dst)
    
modes = [BackupMode('backup', 'm'),
         Mode('work', 'mdD'),
         Mode('transfer', 'mdD'),
         Mode('tree', 'm')]



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
    retMode = None
    for mode in modes:
        #print("lOOP")
        try:
            opts, args = getopt.getopt(arguments[1:], mode.options, [mode.name])
            opts = [opt[0] for opt in opts]
            #print("OPTS: " + str(opts))
            #print("ARGS: " + str(args))
            if ("--" + mode.name) in opts: 
                print("I--" + mode.name)
                retMode = mode
                retMode.options = [x[1] for x in opts if (len(x) == 2
                                                         and x[0] == '-'
                                                         and  x[1] in mode.options)]
                paths = normalizeList(args)
                #print('PPAATTHHSS: ' + str(paths))
                if not paths:
                    printValidSyntaxInfo(arguments[0])
                    return None, None, None
                for path in paths:
                    if not os.path.exists(path):
                        printError('Invalid path: ' + path)
                        return None, None, None
                rootPath = os.path.split(paths[0])[0]
                for path in paths:
                    if rootPath != os.path.split(path)[0]:
                        printError('Given paths must be in the same location')
                        return None, None, None
                
                print("MODE: " + str(retMode))
                return retMode, paths, rootPath
            else:
                print("E--" + mode.name)
        except getopt.GetoptError:
            pass
    #print("getopt.Ge")
    printValidSyntaxInfo(arguments[0])
    return None, None, None

def readConfigurations(configFileName):
    with open(configFileName, 'r') as configFile:
        try:
            configuration = json.load(configFile)
        except json.JSONDecodeError as e:
            printError("Invalid JSON config file: " + configFileName + ":")
            printIndent("Line: " + str(e.lineno) + ", Column: " + str(e.colno) + ", Msg: " + e.msg)
            return None
        return configuration['configs']

def isSubpath(basepath, subpath):
    return  basepath == (os.path.commonpath([basepath, subpath]))

def verifyConfigurations(configs, configFileName):
    if not configs:
        return
    for i, config in enumerate(configs):
        if not 'name' in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config nr ' + str(i) + ' has no field \"name\".')
            return
        elif not 'work' in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config \"' + str(i) + '\" has no field \"work\".')
            return
        elif not 'backup' in config:
            printError("Deficient JSON config file: " + configFileName + ":")
            printIndent('config \"' + str(i) + '\" has no field \"backup\".')
            return
        config['backup'] = normalizeList(config['backup'])
        config['work'] = normalizeList(config['work'])
        for k, w1 in enumerate(config['work']):
            for l, w2 in enumerate(config['work']):
                if k != l and isSubpath(w1, w2):
                    printError('Bad work paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in work cannot be its subpaths or identical.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, b2 in enumerate(config['backup']):
                if k != l and isSubpath(b1, b2):
                    printError('Bad backup paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in backup cannot be its subpaths or identical.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, w2 in enumerate(config['work']):
                #print('b1: ' + b1 + 'w2: ' + w2)
                if k != l and isSubpath(b1, w2):
                    printError('Bad backup or work paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in backup and work cannot be its subpaths or identical.')
                    return
    return configs
    
def filterConfig(config, path):
    config['fWork'] = []
    config['fBackup'] = []
    #print('config_IN: ' +str(config))
    config['fWork'] = [wPath for wPath in config['work'] if isSubpath(wPath, path)]
    config['fBackup'] = [bPath for bPath in config['backup'] if isSubpath(bPath, path)]
    #print('P: '+path+'W: '+str(config['fWork'])+'B: '+str(config['fBackup']))
    #print('config_OUT: ' +str(config))
    return config

def userSelectConfig(configs):
    if not configs:
        return
    if len(configs) == 1:
        return configs[0]
    print('Many configs applicable, select one (Q to cancel and exit):')
    for configNumber, config in enumerate(configs):
        if config['fWork']:
            print('[' + str(configNumber) + '] in WORK of ' + config['name'] + ': ')
        if config['fBackup']:
            print('[' + str(configNumber) + '] in BACKUP of ' + config['name'] + ': ')
        #print('   WORK:   ' + str(config['work'])) 
        #print('   BACKUP: ' + str(config['backup']))
    num = userSelect(len(configs))
    #print('num: ' + str(num))
    #print('configs' + str(configs))
    if num is None:
        return
    return configs[num]

def filterApplicableConfigs(configs, paths):
    applicableConfigs = []
    for config in configs:
        pathsConfig = [filterConfig(copy(config), path) for path in paths]
        #print('config.NAME: ' +config['name'])
        #print('pathsConfig: ' +str(pathsConfig))
        if [True for pConfig in pathsConfig if (not pConfig['fBackup'] and not pConfig['fWork'])]:
            #At least one path not in BACKUP and not in WORK
            continue
        if not configsEqual(pathsConfig):
            printError('In config: ' + config['name'] + ':')
            printIndent('All given paths should be in the same WORK xor BACKUP')
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
    print('DEBUG SEL: ' + str(applicable))
    if not applicable:
        return -1
    if not mode.loadAndCheck(applicable):
        return -1
    mode.calculateSrcsAndDsts(paths, rootPath)
    mode.perform();

    print("APPLICABLE:")
    print(str(applicable))
    print("MODE:" + str(vars(mode)))
    print("PATHS:" + str(paths))
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))

    

if __name__ == "__main__":
    main(sys.argv)
