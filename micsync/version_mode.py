# /usr/bin/python
from .mode import Mode
from .user import User
from .version import __version__


class VersionMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        pass

    def calculateSrcsAndDsts(self, paths, rootPath):
        pass

    def perform(self):
        User.print_info(__version__)

