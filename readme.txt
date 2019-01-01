What micsync can do?

There are two types of locations:
	-WORKING: Location where only some files are kept and changes are made by user.
	-BACKUP: It is a copy of what's in WORKING, but also data saved there in past.

WORKING can be linked with one or more BACKUPS. There may be many WORKING LINKED sharing same BACKUP.

Supported actions location (WORKING or BACKUP):
		-backup:
			Asks which WORKING to choose if many are accessible.
			Copies selected from WORKING to all accesible BACKUPS.
			It never deletes anything in BACKUP. Lists new.
			Lists modified and asks for confirmation.
			Options:
			-m Copy modified without asking.
		-work:
			Asks which WORKING and/or BACKUP to chooseif many are accesible.
			Copies selected from chosen BACKUP to chosen WORKING.
			Lists modified and asks for confirmation.
			Lists to-delete and asks for confirmation.
			Options:
			-m Copy modified without asking.
			-d Allows deleting files in WORKING.
			-D Delete without asking (-d option not needed).
		-transfer
			Asks to confirm or choose destination and source BACKUPS. 
			Copies selected from chosen src BACKUP to chosen dst BACKUP.
			Lists modified and asks for confirmation.
			Lists to-delete and asks for confirmation.
			Options:
			-m Copy modified without asking.
			-d Allows deleting files in dst BACKUP.
			-D Delete without asking (-d option not needed).
		-tree
			Copy directies empty structure from backup to work r update existing.
