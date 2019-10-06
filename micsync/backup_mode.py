#!/usr/bin/python
from .mode import Mode
from .user import User


class BackupMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable["fBackup"]:
            self.applicable["srcLocation"] = User.select_location(
                self.applicable["work"], "WORK")
        else:
            self.applicable["srcLocation"] = self.applicable["fWork"][0]
        if not self.applicable["srcLocation"]:
            return
        self.applicable["dstLocations"] = self.applicable["backup"]
        return True
