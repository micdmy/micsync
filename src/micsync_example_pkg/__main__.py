# /usr/bin/python

import sys
from .micsync import Micsync
name = "micsync_example_pkg"


class MicsyncFriend(Micsync):



program = Micsync(None, None, None)
if program._init_with_arguments(sys.argv):
    program.sync()
