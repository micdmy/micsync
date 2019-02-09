#/usr/bin/python

import sys, getopt, json, os.path


class Mode:
    def __init__(self, name, options):
        self.name = name
        self.options = options

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
    modes = [Mode('backup', 'm'),
             Mode('work', 'mdD'),
             Mode('transfer', 'mdD'),
             Mode('tree', 'm')]
    for mode in modes:
        try:
            opts, args = getopt.getopt(arguments[1:], mode.options, [mode.name])
            retMode = mode
            retMode.options = [x[0][1] for x in opts if (len(x[0]) == 2
                                                     and x[0][0] == '-'
                                                     and  x[0][1] in mode.options)]
            paths = [os.path.abspath(arg) for arg in args]
            for path in paths:
                if not os.path.exists(path):
                    printError('Invalid path: ' + path)
                    return None, None
            return retMode, args
        except getopt.GetoptError:
            pass
    printError('Valid syntax is:')
    for mode in modes:
        optString = ''
        for char in mode.options:
            optString += ' [-' + char + ']'
        printIndent(arguments[0] + ' --' + mode.name + optString + ' path...')
    return None, None

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
    basepath = os.path.abspath(basepath)
    subpath = os.path.abspath(subpath)
    return  basepath == (os.path.commonpath([basepath, subpath]))
    
def filterConfig(config, path):
    config['fWork'] = [wPath for wPath in config['work'] if isSubpath(wPath, path)]
    config['fBackup'] = [bPath for bPath in config['backup'] if isSubpath(bPath, path)]
    return config

def userSelectConfig(configs,):
    if not configs:
        return
    if len(configs) == 1:
        return configs[0]
    print('Many configs applicable, select one (Q to cancel and exit):')
    configNumber = 0
    for config in configs:
        if config['fWork']:
            print('[' + str(configNumber) + '] in WORK of ' + config['name'] + ': ')
        if config['fBackup']:
            print('[' + str(configNumber) + '] in BACKUP of ' + config['name'] + ': ')
        print('   WORK:   ' + str(config['work'])) 
        print('   BACKUP: ' + str(config['backup']))
        configNumber += 1
    while True:
        userInput = input('[0-' + str(len(configs) - 1) + ']')
        if userInput.isnumeric() and int(userInput) in (0, len(configs) - 1):
            return configs[int(userInput)]    
        elif userInput.isalpha() and userInput in 'Qq':
            return 

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
    mode, paths = parseInputArguments(argv)
    if not mode or not paths :
        return -1
    configs = readConfigurations('./.micsync.json')
    if not configs:
        return -1
    applicables = filterApplicableConfigs(configs, paths)
    if not applicables:
        return -1
    applicable = userSelectConfig(applicables)
    if not applicable:
        return -1
        
    print(str(applicable))
        
    print("MODE:" + str(vars(mode)))
    print("PATHS:" + str(paths))
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))
    print("TEST")

    

if __name__ == "__main__":
    main(sys.argv)
