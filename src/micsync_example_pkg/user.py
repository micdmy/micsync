# /usr/bin/python


class User:
    def __init__(self):
        pass

    @classmethod
    def decide(cls, msg, true_response, false_response):
        while True:
            prompt = msg + "[" + true_response + "/" + false_response + "]"
            user_input = input(prompt)
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
        text = "Choose " + location_name + " location (Q to cancel and exit):"
        User.print_in_newline(text)
        for i, loc in enumerate(location):
            User.print_info("[" + str(i) + "] " + loc)
        num = User._select(len(location))
        if num is None:
            return
        User.print_in_newline("SELECTED: " + str(location[num]))
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
        num = User._select(len(configs))
        if num is None:
            return
        return configs[num]

    @classmethod
    def _select(cls, num_elem):
        while True:
            user_input = input("[0-" + str(num_elem - 1) + "]")
            if user_input.isnumeric() and \
                    int(user_input) in list(range(0, num_elem)):
                return int(user_input)
            elif user_input.isalpha() and user_input in "Qq":
                return

    @classmethod
    def print_error(cls, msg):
        print("micsync.py: Error: " + str(msg))

    @classmethod
    def print_info(cls, msg):
        print(str(msg))

    @classmethod
    def print_in_newline(cls, msg):
        print('\n' + str(msg))

    @classmethod
    def print_indent(cls, msg):
        print("    " + str(msg))
