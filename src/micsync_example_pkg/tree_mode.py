# /usr/bin/python
from .work_mode import WorkMode
from .rsync import Rsync


class TreeMode(WorkMode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def perform(self):
        for dst in self.dsts:
            options = self.flags.getRsyncOptions(dst, self.srcs) + Rsync.TREE
            Rsync.sync(self.srcs, dst, options, self.flags.verbose)

