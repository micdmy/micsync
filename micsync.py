#/usr/bin/python

import sys, getopt, json

class Mode:
    def __init__(self, name, options):
        self.name = name
        self.options = options

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
            return retMode
        except Exception as e:
            pass
    print('micsync.py: Valid syntax is:')
    for mode in modes:
        optString = ''
        for char in mode.options:
            optString += ' [-' + char + ']'
        print(arguments[0] + ' --' + mode.name + optString)
    return None

def readConfigurations(configFileName):
    with open(configFileName, 'r') as configFile:
        configuration = json.load(configFile)
        return configuration['configs']
    print("Error: reading: " + configFileName)
    return None

def main(argv):
    mode = parseInputArguments(argv)
    if mode is None:
        return -1
    print("MODE:" + str(vars(mode)))
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))
    

if __name__ == "__main__":
    main(sys.argv)
