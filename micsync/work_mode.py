# /usr/bin/python
from .mode import Mode
from .user import User


class WorkMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if self.applicable["fBackup"]:
            self.applicable["dstLocations"] = [
                User.select_location(self.applicable["work"], "WORK")]
            self.applicable["srcLocation"] = self.applicable["fBackup"][0]
        else:
            self.applicable["dstLocations"] = [self.applicable["fWork"][0]]
            self.applicable["srcLocation"] = User.select_location(
                self.applicable["backup"], "BACKUP")
        if self.applicable["dstLocations"][0] \
                and self.applicable["srcLocation"]:
            return True
        return
