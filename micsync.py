#/usr/bin/python

import sys, getopt

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'mdD', ['backup', 'work', 'transfer', 'tree'])
    except getopt.GetoptError:
        print('exeption')
    print('opts:', str(opts))
    print('ARGS:', str(args))

if __name__ == "__main__":
    main(sys.argv[1:])
