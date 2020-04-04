# Automatic test for micsync
Currenly tests cover only a very basic functionalities of micsync.
Nevertheless it's worth to run tests after a build of new version of program.

## How to run automatic tests
Required packages:
* `pytest`

Steps:
1. Install micsync. Clone or download micsync repository.
2. Make sure your current directory is the repository directory
3. Run `pytest`
4. See the results.

## What is covered by the automatic tests:
* `test_installation.py` - Checks if micsync was succesfully installed in the current environment.
  - Checks with `pacman` package manager.
  - Checks with `pip` python package manger.
  - Checks if `micsync --version` can be succesfully called.
  - Check if python module can be executed with `python -m micsync --version`.

* `test_init.py` - It's under development. Provides api for cehcking various micsync commands.

