# /usr/bin/python


class User:
    def __init__(self):
        pass

    @classmethod
    def decide(cls, msg, true_response, false_response):
        while True:
            user_input = input(msg + "[" + true_response + "/" + false_response + "]")
            if user_input:
                if user_input.upper() == true_response.upper():
                    return True
                elif user_input.upper() == false_response.upper():
                    return False

    @classmethod
    def select_location(cls, location, location_name):
        if not location:
            return
        if len(location) == 1:
            return location[0]
        printInNewline("Choose " + location_name +
                       " location (Q to cancel and exit):")
        for i, loc in enumerate(location):
            printInfo("[" + str(i) + "] " + loc)
        num = _select(len(location))
        if num is None:
            return
        printInfo("SELECTED: " + str(location[num]))
        return location[num]

    @classmethod
    def select_config(cls, configs):
        if not configs:
            return
        if len(configs) == 1:
            return configs[0]
        print("Many configs applicable, select one (Q to cancel and exit):")
        for config_number, config in enumerate(configs):
            if config["fWork"]:
                print("[" + str(config_number) + "] in WORK of " +
                      config["name"] + ": ")
            if config["fBackup"]:
                print("[" + str(config_number) + "] in BACKUP of " +
                      config["name"] + ": ")
        num = _select(len(configs))
        if num is None:
            return
        return configs[num]

    @classmethod
    def _select(cls, num_elem):
        while True:
            user_input = input("[0-" + str(num_elem - 1) + "]")
            if user_input.isnumeric() and int(user_input) in list(range(0, num_elem)):
                return int(user_input)
            elif user_input.isalpha() and user_input in "Qq":
                return

# def printError(msg):
    @classmethod
    def print_error(cls, msg):
        print("micsync.py: Error: " + str(msg))


# def printInfo(msg):
    @classmethod
    def print_info(cls, msg):
        print(str(msg))


# def printInNewline(msg):
    @classmethod
    def print_in_newline(cls, msg):
        print('\n' + str(msg))


# def printIndent(msg):
    @classmethod
    def print_indent(cls, msg):
        print("    " + str(msg))

