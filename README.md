# MICSYNC - local discs synchronisation tool
Micsync is a tool that provides easy management of data kept on the disc and its backup or backups.
It uses rsync for all file operations. Verbose option will show the exact rsync command used.

micsync on PyPi: [https://pypi.org/project/micsync/](https://pypi.org/project/micsync/)

# Installation
If you are using pacman package manager (on Arch linux and derived systems), prefer installation with pacman over pip. If you install package with pip, pacman doesn't see it and it may lead to conflicts in future when installing or updating other packages.

## Using git and makepkg (for pacman users)
```bash
git clone https://github.com/micdmy/micsync.git
cd micsync/archive-pkgbuild/<last version>/
makepkg -sir
```
Replace `<last version>` with actual directory name.

Learn more: [git clone](https://git-scm.com/docs/git-clone) [makepkg](https://wiki.archlinux.org/index.php/Makepkg)

## Using pip
As root:
```
	pip install micsync
```
Learn more: [python - installing packages](https://packaging.python.org/tutorials/installing-packages/)

## Using git and python-setuptools
```bash
git clone https://github.com/micdmy/micsync.git
cd micsync/
./build.sh
cd output/offline-PKGBUILD/
tar -xzf micsync*
cd micsync*/
```

As root:
```bash
python setup.py install --optimize=1
```

## Check if micsync was installed succesfully
```bash
micsync --version
```

# How to use it
Micsync allows to configure WORKING and BACKUP locations.
Location is a directory in filesystem and all subdirectories and files it contains.

There are two types of locations which serve different purposes:

* WORKING location - examples of use
  - Location on disc that's backup can be kept in BACKUP.
  - Workplace from which some files/directories can be send to BACKUP.
  - Temporary cache for some data needed at the moment, that are kept on BACKUP all the time (i.e. when BACKUP is on external hard disc).

* BACKUP location - examples of use
  - Can be used as backup copy of things in WORKING location.
  - Can be used as source of data for other BACKUPs (mirrors).
  - Data from BACKUP can be copied back to WORKING, or even override or remove data there.
  - BACKUP directories structure (tree, skeleton) can be copied (without files) to WORKING.

Any number of WORKINGs can be linked with any number of BACKUPs.
One CONFIGURATION links together WORKINGs and BACKUPs.
WORKINGs and BACKUPs in one CONFIGURATION cannot overlap (i.e. WORKING contains BACKUP).

There may be a lot of CONFIGURATIONs that don't influence each other.
User sets the CONFIGURATIONs up in ".micsync.json" file located in user's home directory.

Example of .micsync.json file:
```json
{
  "configs": [
   {
    "name": "My first CONFIGURATION, it contains 1 WORKING and 1 BACKUP",
    "work": [
    	"/home/example_user/some_dir/"
    ],
    "backup": [
    	"/example/path/"
    ]
   },
   {
    "name": "My second CONFIGURATION, it contains 2 WORKINGs and 3 BACKUPs",
    "work": [
    	"/home/example_user/some_dir/",
    	"~/other/"
    ],
    "backup": [
    	"/a/backup/",
    	"./it/may/be/relative/path/",
    	"~/my/third/backup/"
    ]
   }
  ]
}
```

## Command line interface

### Command syntax
```bash
micsync <sync-action> [options] <paths>
```
```bash
micsync <other-action>
```

`<sync-action>` tells micsync what kind of the synchronization operation should be performed between locations.
Currently, there are 4 synchronization actions defined:
* `--backup`
* `--work`
* `--transfer`
* `--tree`

`<other-action>` are actions that don't perform any operations on files in defined locations:
* `--version` - prints the program version

`[options]` are specific for each action.
They are used, for example, to define what micsync do with modified files or if it can delete files.

`<paths>` is a path or space-separated list of paths to directories or files that exist within some of defined configurations.
All of the given paths must be within defined configurations.

It doesn't matter if a path is in WORKING or BACKUP location. It doesn't influence the direction of copying.
You can tell micsync to, for example, do `--backup` operation, specifying path in BACKUP or in WORKING. In each case, copying from WORKING to BACKUP will be performed. The direction is defined by `<sync-action>`, not by `<paths>`.

### Synchronization actions
* `--backup`
  - Copies files and directories in `<paths>` from WORKING to all accessible BACKUPs.
  - Asks which WORKING to choose if many are accessible.
  - It never deletes anything in BACKUP. Lists new.
  - Lists modified and asks for confirmation.
  - Options: `-m -s -v`
  - Source: WORKING
  - Destination: all accessible BACKUPS

* `--work`
  - Copies files and directories in `<paths>` from chosen BACKUP to chosen WORKING.
  - Asks which WORKING and/or BACKUP to choose if many are accessible.
  - Lists to-delete and asks for confirmation.
  - Lists modified and asks for confirmation.
  - Options: `-m -d -D -s -v`
  - Source: WORKING
  - Destination: BACKUP

* `--transfer`
  - Copies files and directories from chosen src BACKUP to chosen dst BACKUP.
  - Asks to confirm or choose destination and source BACKUPS.
  - Lists to-delete and asks for confirmation.(Only if -d ? - TODO: check it)
  - Lists modified and asks for confirmation.
  - Options: `-m -d -D -s -v`
  - Source: BACKUP
  - Destination: BACKUP

* `--tree`
  - Copy directories empty structure from backup to work and/or update existing.
  - Options: `-s -v`
  - Source: BACKUP
  - Destination: WORKING

### Options for synchronization actions
Copying options:

* `-m` Copy modified (overwrite) without asking.
* `-d` Delete files in dst if they don't exist in src. Ask before deleting.
* `-D` Delete files in dst if they don't exist in src. Don't ask before deleting. If `-d` and `-D` specified, works as if only `-D` was specified.

User interface and verbosity options:

* `-s` Suppress information about modifying directories.
* `-v` Verbose mode. Shows rsync command used to perform synchronization. Asks before doing anything.

# Bug reporting
Have you found a bug? Please, report it [here](https://github.com/micdmy/micsync/issues).

# Information for developers
If you are a developer and want to contribute to micsync, you're welcomed!
Don't hesitate to contact the author if you have questions.

Required software:
* `linux operating system`
* `rsync`
* `pacman`
* `python >= 3.7` 
* `python-pip`
* `python-pytest`
* `python-wheel`
* `twine`
* `git`

## Getting source code
`git clone https://github.com/micdmy/micsync.git`

## Workflow - development and testing on local machine
1. Make the changes.
2. Run `./build.sh` and see if there are any errors in output.
3. Enter the directory with package for local (offline) installation: `cd output/offline-PKGBUILD/`
4. Install with makepkg: `makepkg -sir`
5. Run tests from main repository directory. See: [tests/README.md](https://github.com/micdmy/micsync/tree/master/tests/README.md).
6. Do some manual tests.
7. Commit/push changes.

## Workflow - releasing version
1. You're ready with 'development and testing on local machine'.
2. Change version number in file [micsync/version.py](https://github.com/micdmy/micsync/tree/master/micsync/version.py).
3. Clean previous build artifacts with `./clean.sh`.
4. Run `./build.sh`. You will be warned that git tag is not updated. Ignore it, press `y` and enter. See if there are any errors in output.
5. Run `./deploy-pip.sh`. `output/dist/micsync-0.0.4.dev0-py3-none-any.whl` and `output/dist/micsync-0.0.4.dev0.tar.gz` will be sent to `https://pypi.org/project/micsync/`. You will be asked for credentials.
5. Run `./deploy-aur.sh`. PKGBUILD file will be added to `archive-pkgbuild/<new version>/`.
6. Stage `archive-pkgbuild/` and `micsync/version.py`.
7. Commit, add tag `<new version>` and push with tags.

## Workflow - testing released version
1. Uninstall old version of micsync with pacman or pip.
2. Install new version with pip. Run automatic tests. Make manual tests. Uninstall micsync.
3. Install new version with pacman or makepkg. Run automatic tests. Make manual tests.

## Project organization
Directory / File | In git repo | Purpose
--------- | ---- | -------
`./micsync/` | Yes. | Source code.
`./micsync/version.py` | Yes | Contains version and program name. Version from this file is taken as program version by `build.sh`
`.tests/` | Yes. | Automatic tests source code.
`./archive-pk-pkgbuild/` | Yes. | Storage for PKGBUILD files for every version.
`./output/` |  No. | After build, contains all build artifacts. Removed with `clean.sh`
`./output/offline-PKGBUILD/` | No. | After build, contains the packaged program and specially prepared PKGBUILD file for local (offline) installation.
`./build.sh` | Yes. | Script that builds the program.
`./clean.sh` | Yes. | Script that cleans the build artifacts.
`./deploy-aur.sh` | Yes | Script that copies `output/PKGBUILD` to `archive-pkgbuild/<new version>/`.
`./deploy-pip.sh` | Yes | Script that sends new version to PyPi/[micsync](https://pypi.org/project/micsync/).
`./micsync/version.py` | Yes | Contains version and program name. Version from this file is taken as program version by `build.sh`