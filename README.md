micsync is a tool that provides easy management of data kept on the disc and its backup or backups.
It uses rsync for all file operations. Verbose option will show the exact rsync command used.

micsync allows to configure WORKING and BACKUP locations.
Location is a directory in filesystem and all subdirectories and files it contains.
There are two types of locations which serve different purposes:
	WORKING: 
		-Location on disc that's backup can be kept in BACKUP.
		-Workplace from which some files/directories should be send to BACKUP.
		-Temporary cache for some data needed at the moment, that are kept on BACKUP all the time (i.e. BACKUP is on external hard disc).
	BACKUP:
		-Can be used as backup copy of things in WORKING location.
		-Can be used as source of data for other BACKUPs (mirrors).
		-Data from backup can be copied back to WORKING, or even overide or remove data there.
		-BACKUP directories structure (tree, skeleton) can be copied (without files) to WORKING.

Any number of WORKINGs can be linked with any number of BACKUPs.
One CONFIGURATION links together WORKINGs and BACKUPs.
WORKINGs and BACKUPs in one CONFIGURATION cannot overlap (i.e. WORKING contains BACKUP).

There may be a lot of CONFIGURATIONs that don't influence each other.
User sets the CONFIGURATIONs up in ".micsync.json" file 
Example structure of file:
{
		"configs": [ {
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

Supported actions location (WORKING or BACKUP):
		-backup:
			Asks which WORKING to choose if many are accessible.
			Copies selected from WORKING to all accesible BACKUPS.
			It never deletes anything in BACKUP. Lists new.
			Lists modified and asks for confirmation.
			Options:
			-m Copy modified without asking.
			-s Suppress information about modifying directories.
			-v Verbose mode.
		-work:
			Asks which WORKING and/or BACKUP to choose if many are accesible.
			Copies selected from chosen BACKUP to chosen WORKING.
			Lists modified and asks for confirmation.
			Lists to-delete and asks for confirmation.
			Options:
			-m Copy modified without asking.
			-d Allows deleting files in WORKING.
			-D Delete without asking (-d option not needed).
			-s Suppress information about modifying directories.
			-v Verbose mode.
		-transfer
			Asks to confirm or choose destination and source BACKUPS. 
			Copies selected from chosen src BACKUP to chosen dst BACKUP.
			Lists modified and asks for confirmation.
			Lists to-delete and asks for confirmation.
			Options:
			-m Copy modified without asking.
			-d Allows deleting files in dst BACKUP.
			-D Delete without asking (-d option not needed).
			-s Suppress information about modifying directories.
			-v Verbose mode.
		-tree
			Copy directies empty structure from backup to work r update existing.
			Options:
			-s Suppress information about modifying directories.
			-v Verbose mode.

How to instal with pip:

python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-pkg-your-username
