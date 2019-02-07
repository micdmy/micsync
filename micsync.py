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

def allEqual(elements):
    return len(set(elements)) in (0, 1)

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
    config['work'] = [wPath for wPath in config['work'] if isSubpath(wPath, path)]
    config['backup'] = [bPath for bPath in config['backup'] if isSubpath(bPath, path)]
    return config

def main(argv):
    mode, paths = parseInputArguments(argv)
    if not mode or not paths :
        return -1
    configs = readConfigurations('./.micsync.json')
    if not configs:
        return -1
    
    for config in configs:
        pathsConfig = [filterConfig(config, path) for path in paths]

////////////////////////////////////////////////////////////////
TODO refactor
    filtered = [filterConfig(configs, path) for path in paths]
    print(type(filtered))
    print(type(filtered[0]))

    print(str(filtered))
    if any([(not f['work'] and not f['backup']) for f in filtered]):
        printError('All of paths given should be configured as WORK xor BACKUP.')
    elif not allEqual(filtered):
        printError('All given paths should be in the same WORK xor BACKUP.')
    elif filtered[0]['work'] and filtered[0]['backup']:
        printError('Given paths cannot be both in WORK and BACKUP.') 
    else:
        print('ALL OK')
/////////////////////////////////////////////////////////////////
    print(str((filtered)))
    print("MODE:" + str(vars(mode)))
    print("PATHS:" + str(paths))
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))
    print("TEST")

    

if __name__ == "__main__":
    main(sys.argv)
