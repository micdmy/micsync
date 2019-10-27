import subprocess
import pytest


@pytest.fixture
def execute(capfd):
    def _execute(arguments):
        subprocess.run(args = arguments)
        return capfd.readouterr()
    return _execute

@pytest.fixture
def execute_success(execute):
    def _execute_success(arguments):
        out, err = execute(arguments)
        assert not err
        return out
    return _execute_success

@pytest.fixture
def version_regex():
    return "([0-9]+\\.[0-9]+\\.[0-9]+)(\\.dev[0-9]+(-[0-9]+)*)"

@pytest.fixture
def program_name():
    return "micsync"

