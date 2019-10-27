from collections import OrderedDict


class InitTestCases:

    class TestCasesException(Exception):
        pass

    def __init__(self):
        invalid_operations = InitTestCases._find_invalid_operations()
        if invalid_operations:
            raise InitTestCases.TestCasesException({
                "message": "Invalid operations in test_cases.", "invalid_operations:": invalid_operations})
    
    valid_operations = ["c_mode",
                        "c_options",
                        "c_paths",
                        "s_mode",
                        "s_options",
                        "s_paths",
                        "s_config",
                        "_help",
                        "sync"]

    test_cases = [
        OrderedDict(_help = None), 
        OrderedDict(c_mode = "WORK", c_paths = ["foo.bar", "bar.foo"]),
        OrderedDict(c_mode = "BACKUP", c_paths = ["foo.bar", "bar.foo"])
        ]

    @classmethod
    def _find_invalid_in_case(cls, case):
        return [oper for oper in list(case.keys()) if oper not in cls.valid_operations]

    @classmethod
    def _find_invalid_operations(cls):
        return [cls._find_invalid_in_case(case) for case in cls.test_cases if cls._find_invalid_in_case(case)]



class TestInit():

    def test_as_module(self):
        self.init_test_cases = InitTestCases();
        init_strategy = 

    
    

class InitStrategy():
    def __init__(self, init_test_cases):
        self.init_test_cases = init_test_cases


class InitModule(InitStrategy):
    def __init__(self, init_test_cases):
        super().__init__(init_test_cases)
        self.program_name = "micsync"
        self.operations_two_dashes = ["help"]
        self.operations_with_dash = ["c_options", "s_options"]

    def init(self):
        
    def _parse_bash_command(self, test_case):
        command = program_name
        for operation_name, operation in test_case.item():
            if operation_name in ["help"]
            command.append(" " + operation)
    
    def _add_dashes_if_needed(self, operation_name)

        
