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
            opts, args = getopt.getopt(argv, mode.options, [mode.name])
            return mode
        except Exception:
            pass
    print('micsync.py: Valid syntax is:')
    for mode in modes:
        optString = ''
        for char in mode.options:
            optSting += ' [-' + char + ']'
        print('--' + mode.name + optString)
    return None

def readConfigurations(configFileName):
    with open(configFileName, 'r') as configFile:
        configuration = json.load(configFile)
        return configuration['configs']
    print("Error: reading: " + configFileName)
    return None

def main(argv):
    parseInputArguments(argv)
    print("READING JSON:")
    print(readConfigurations('./.micsync.json'))
    

if __name__ == "__main__":
    main(sys.argv[1:])
