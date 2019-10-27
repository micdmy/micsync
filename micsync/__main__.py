#!/usr/bin/python

import sys
from .micsync import Micsync
name = "micsync"


class MicsyncFriend(Micsync):
    def __init__(self, mode_name, options, paths):
        super().__init__(mode_name, options, paths)

    def init_with_arguments(self, arguments):
        return super()._init_with_arguments(arguments)


program = MicsyncFriend(None, None, None)
if program.init_with_arguments(sys.argv):
    program.sync()

