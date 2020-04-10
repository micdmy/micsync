from test_common_fixtures import *
import re

class TestInstallation():

    def test_installed_in_pacman(self, execute_success, version_regex, program_name):
        out = execute_success(["pacman", "-Q", program_name])
        assert re.search("(" + program_name + "\\s*)" + version_regex + "(\\s*)", out)

    def test_installed_binary(self, execute_success, version_regex, program_name):
        out = execute_success([program_name, "--version"])
        assert re.search(version_regex + "(\\s*)", out) is not None

    def test_installed_module(self, execute_success, version_regex, program_name):
        out = execute_success(["python", "-m", program_name, "--version"])
        assert re.search(version_regex + "(\\s*)", out) is not None

    def test_installed_pip(self, execute_success, version_regex, program_name, capfd):
        out = execute_success(["pip", "show", program_name])
        out_lines = out.splitlines()
        out_dict = {}
        for line in out_lines:
            split = re.split("(?:\\: )", line, maxsplit = 1)
            assert split
            assert len(split) == 2
            out_dict[split[0]] = split[1]
        pip_expected_result = {
                "Name" : program_name,
                "Version" : version_regex,
                "Summary" : "Local data synchronization tool based on rsync.",
                "Home-page" : "https://github.com/micdmy/micsync/",
                "Author" : "micdmy",
                "Author-email" : "micdmy2@gmail.com",
                "License" : "GPLv3",
                "Location" : ".*",
                "Requires" : "",
                "Required-by" : "",
                }
        assert out_dict.keys() == pip_expected_result.keys()
        for key in list(pip_expected_result.keys()):
            assert re.fullmatch(pip_expected_result[key], out_dict[key]) is not None

