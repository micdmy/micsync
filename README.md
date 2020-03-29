# MICSYNC - local discs synchronisation tool
Micsync is a tool that provides easy management of data kept on the disc and its backup or backups.
It uses rsync for all file operations. Verbose option will show the exact rsync command used.

# Installation

## Using pip
```
	pip install micsync
```
Learn more: [python - installing packages](https://packaging.python.org/tutorials/installing-packages/)

## Using makepkg (for pacman users)
```
git clone https://github.com/micdmy/micsync.git
cd micsync/archive-pkgbuild/[last version]/
makepkg -sir
```
Learn more: [git clone](https://git-scm.com/docs/git-clone) [makepkg](https://wiki.archlinux.org/index.php/Makepkg)

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
  - Data from BACKUP can be copied back to WORKING, or even overide or remove data there.
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

`<sync-action>` tells micsync what kind of the syncronization operation should be performed between locations.
Currently, there are 4 syncronization actions defined:
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

### Syncronisation actions
* `--backup`
  - Copies files and directories in `<paths>` from WORKING to all accesible BACKUPs.
  - Asks which WORKING to choose if many are accessible.
  - It never deletes anything in BACKUP. Lists new.
  - Lists modified and asks for confirmation.
  - Options: `-m -s -v`
  - Source: WORKING
  - Destination: all accessible BACKUPS

* `--work`
  - Copies files and directories in `<paths>` from chosen BACKUP to chosen WORKING.
  - Asks which WORKING and/or BACKUP to choose if many are accesible.
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
  - Copy directies empty structure from backup to work and/or update existing.
  - Options: `-s -v`
  - Source: BACKUP
  - Destination: WORKING

### Options for syncronization actions
Copying options:

* `-m` Copy modified (overwrite) without asking.
* `-d` Delete files in dst if they don't exist in src. Ask before deleting.
* `-D` Delete files in dst if they don't exist in src. Don't ask before deleting. If `-d` and `-D` specified, works as if only `-D` was specified.

User interface and verbosity options:

* `-s` Suppress information about modifying directories.
* `-v` Verbose mode. Shows rsync command used to perform synchronization. Asks before doing anything.
