from collections import OrderedDict


class InitCases:

    class CasesException(Exception):
        pass

    def __init__(self):
        invalid_operations = InitCases._find_invalid_operations()
        if invalid_operations:
            raise InitCases.CasesException({
                "message": "Invalid operations in test_cases.", "invalid_operations:": invalid_operations})
    
    # c_ -constructor argument
    # s_ -setter argument
    valid_operations = ["c_mode",
                        "c_options",
                        "c_paths",
                        "c_config",
                        "s_mode",
                        "s_options",
                        "s_paths",
                        "s_config",
                        "_help",
                        "sync"]

    test_cases = [
        OrderedDict(_help = None), 
        OrderedDict(c_mode = "WORK", c_paths = ["foo.bar", "bar.foo"]),
        OrderedDict(c_mode = "BACKUP", c_paths = ["foo.bar", "bar.foo"]),
        OrderedDict(s_mode = "TREE", c_options = "dsdsad", s_options = ["aaa", "dfsd dff"], s_paths = "dsds", s_config = "CONF", c_config = ["CCC", "C_CON"], _help = "dsjkdjHELP", sync = "NIE POWINNO BYC MNIE WIDAC"),
        OrderedDict(c_mode = "BACKUP", c_options = ["c", "n", "b"]),
        OrderedDict(c_mode = "BACKUP", c_options = ["cfdasf", "nfdf", "bGGG"])
        ]

    def __iter__(self):
        return CasesIterator(self)

    @classmethod
    def _find_invalid_in_case(cls, case):
        return [oper for oper in list(case.keys()) if oper not in cls.valid_operations]

    @classmethod
    def _find_invalid_operations(cls):
        return [cls._find_invalid_in_case(case) for case in cls.test_cases if cls._find_invalid_in_case(case)]

    @classmethod
    def stringize(cls, string_or_list_of_string, separator = ""):
        if type(string_or_list_of_string) == str:
            return string_or_list_of_string
        elif type(string_or_list_of_string) == list and type(string_or_list_of_string[0]) == str:
            return str(separator.join(string_or_list_of_string))
        return ""




class CasesIterator:
    def __init__(self, test_cases):
        self._test_cases = test_cases
        self._idx = 0

    def __next__(self):
        if self._idx < len(self._test_cases.test_cases):
            result = self._test_cases.test_cases[self._idx]
            self._idx += 1
            return result
        raise StopIteration


class TestInit():

    def test_as_module(self, capfd):
        self.init_strategy = InitModule(InitCases())
        with capfd.disabled():
            self.init_strategy.perform_test_cases_list()

    
    

class InitStrategy():
    def __init__(self, test_cases):
        self.test_cases = test_cases

    def perform_test_cases_list(self):
        pass



class InitModule(InitStrategy):
    def __init__(self, init_test_cases):
        super().__init__(init_test_cases)
        self.program_name = "micsync"
        self.operations_two_dashes = ["help"]
        self.operations_with_dash = ["c_options", "s_options"]

    def perform_test_cases_list(self):
        for test_case in self.test_cases:
            print("+++++++++++++++++++")
            print(str(test_case))
            self._parse_bash_command(test_case)
        
    def _parse_bash_command(self, test_case ):
        command = self.program_name
        for operation_name, operation in test_case.items():
            if operation_name in ["c_mode", "s_mode"]:
                command += " " + InitCases.stringize(operation, " ")
            elif operation_name in ["c_options", "s_options"]:
                command += " -" + InitCases.stringize(operation, " -")
            elif operation_name in ["c_paths", "s_paths"]:
                command += " " + InitCases.stringize(operation, " ")
            elif operation_name in ["c_config", "s_config"]:
                command += " --config-file " + InitCases.stringize(operation, " ")
            elif operation_name in ["_help"]:
                command += " --help " + InitCases.stringize(operation, " ")
            elif operation_name in ["sync"]:
                pass #  nothing changes in command
            else:
                raise InitCases.CasesException({
                    "message": "Invalid operation in test_cases.", "invalid_operation:": operation_name})
            
            print(command + "\n")
    

        
