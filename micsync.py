#/usr/bin/python

import sys, getopt, json, os.path

def userSelect(numElem):
    while True:
        userInput = input('[0-' + str(numElem -1) + ']')
        if userInput.isnumeric() and int(userInput) in (0, numElem - 1):
            return int(userInput)
        elif userInput.isalpha() and userInput in 'Qq':
            return 

def userSelectWork(work):
    if not work:
        return
    if len(work) == 1:
        return work[0]
    print('Choose WORK location (Q to cancel and exit):')
    for i, w in enumerate(work):
        print('[' + str(i) + '] ' + w)
    num = userSelect(len(work))
    if not num:
        return
    return work[num] 

def getAccesiblePaths(paths):
    return [p for p in paths if os.path.exists(p)]

def prependRoot(root, paths):
    return [os.path.join(root, p) for p in paths] 

def makeRelative(root, paths):
    return [os.path.relpath(p, root) for p in paths]

def normalize(path):
    if isinstance(path, list):
        return [os.path.realpath(os.path.abspath(p)) for p in path]
    else:
        return os.path.realpath(os.path.abspath(path))

class Mode:
    def __init__(self, name, options):
        self.name = name
        self.options = options

class BackupMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)
    def loadAndCheck(self, applicable):
        self.applicable = applicable
        if self.applicable['fBackup']:
            self.applicable['sWork'] = userSelectWork(self.applicable('work'))
            self.applicable['pathsOrigin'] = self.applicable['fBackup'][0]
        else:
            self.applicable['sWork'] = self.applicable['fWork'][0]
            self.applicable['pathsOrigin'] = self.applicable['fWork'][0]
        if not self.applicable['sWork']:
            return
        return True
    def perform(self, paths, rootPath):
        relPaths = makeRelative(self.applicable['pathsOrigin'], paths)
        srcs = prependRoot(self.applicable['sWork'], relPaths)
        relRootPath = makeRelative(self.applicable['pathsOrigin'], rootPath)
        for backup in getAccesiblePaths(self.applicable['backup']):
            dst = prependRoot(backup, relRootPath)[0]
            print('SRCS: ' + str(srcs))
            print('DST: ' + dst)
        return True
    
modes = [BackupMode('backup', 'm'),
         Mode('work', 'mdD'),
         Mode('transfer', 'mdD'),
         Mode('tree', 'm')]

def printError(msg):
    print('micsync.py: Error: ' + str(msg)) 

def printIndent(msg):
    print('    ' + str(msg))

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

def parseInputArguments(arguments):
    for mode in modes:
        try:
            opts, args = getopt.getopt(arguments[1:], mode.options, [mode.name])
            retMode = mode
            retMode.options = [x[0][1] for x in opts if (len(x[0]) == 2
                                                     and x[0][0] == '-'
                                                     and  x[0][1] in mode.options)]
            paths = normalize(args)
            print('PPAATTHHSS: ' + str(paths))
            for path in paths:
                if not os.path.exists(path):
                    printError('Invalid path: ' + path)
                    return None, None, None
            rootPath = os.path.split(paths[0])[0]
            for path in paths:
                if rootPath != os.path.split(path)[0]:
                    printError('Given paths must be in the same location')
                    return None, None, None
            return retMode, paths, rootPath
        except getopt.GetoptError:
            pass
    printError('Valid syntax is:')
    for mode in modes:
        optString = ''
        for char in mode.options:
            optString += ' [-' + char + ']'
        printIndent(arguments[0] + ' --' + mode.name + optString + ' path...')
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
        for k, w1 in enumerate(config['work']):
            for l, w2 in enumerate(config['work']):
                if k != l and isSubpath(w1, w2):
                    printError('Bad work paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in work cannot be its subpaths.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, b2 in enumerate(config['backup']):
                if k != l and isSubpath(b1, b2):
                    printError('Bad backup paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in backup cannot be its subpaths.')
                    return
        for k, b1 in enumerate(config['backup']):
            for l, w2 in enumerate(config['work']):
                if k != l and isSubpath(b1, w2):
                    printError('Bad backup or work paths in config \"' + config['name'] + '\"')
                    printIndent('Paths in backup and work cannot be its subpaths.')
                    return
        config['backup'] = normalize(config['backup'])
        config['work'] = normalize(config['work'])
    return configs
    
def filterConfig(config, path):
    config['fWork'] = [wPath for wPath in config['work'] if isSubpath(wPath, path)]
    config['fBackup'] = [bPath for bPath in config['backup'] if isSubpath(bPath, path)]
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
        print('   WORK:   ' + str(config['work'])) 
        print('   BACKUP: ' + str(config['backup']))
    return userSelect(len(configs))

def filterApplicableConfigs(configs, paths):
    applicableConfigs = []
    for config in configs:
        pathsConfig = [filterConfig(config, path) for path in paths]
        if not configsEqual(pathsConfig):
            printError('In config: ' + config['name'] + ':')
            printIndent('All given paths should be the same WORK xor BACKUP')
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
    if mode.loadAndCheck(applicable):
        mode.perform(paths, rootPath)
    else:
        return -1

    print("APPLICABLE:")
    print(str(applicable))
    print("MODE:" + str(vars(mode)))
    print("PATHS:" + str(paths))
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))

    

if __name__ == "__main__":
    main(sys.argv)
