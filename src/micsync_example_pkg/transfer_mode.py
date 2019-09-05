# /usr/bin/python
from .mode import Mode
from .user import User


class TransferMode(Mode):
    def __init__(self, name, options):
        super().__init__(name, options)

    def loadAndCheck(self, applicable):
        if not super().loadAndCheck(applicable):
            return
        if len(self.applicable["backup"]) < 2:
            User.print_info("Bad usage. There must be at least two BACKUP\
                       locations defined for this configuration!")
            return
        self.applicable["srcLocation"] = User.select_location(
            self.applicable["backup"], "SOURCE BACKUP")
        if not self.applicable["srcLocation"]:
            return
        remaining = [bckp for bckp in self.applicable["backup"]
                     if bckp != self.applicable["srcLocation"]]
        self.applicable["dstLocations"] = []
        onlyOneRemainingInitially = len(remaining) == 1
        while True:
            location = User.select_location(remaining, "DESTINATION BACKUP")
            if not location:
                return
            self.applicable["dstLocations"].append(location)
            remaining = [rem for rem in remaining if rem !=
                         self.applicable["dstLocations"][-1]]
            if len(remaining) < 1:
                break
            else:
                if len(remaining) == 1 and not onlyOneRemainingInitially:
                    question = "Do you want to add this DESTINATION BACKUP\
                                location too?\n"
                    if User.decide(question + remaining[0] + "\n", "Y", "N"):
                        self.applicable["dstLocations"].append(remaining[0])
                    break
                else:
                    question = "Do you want to add more DESTINATION BACKUP\
                                locations? "
                    if not User.decide(question, "Y", "N"):
                        break
        return True

