#!/bin/bash

function getCfgFiles {
	echo "$(find ./tests/*.location -type f)"
}

function isSubpath {
	local prefix="$1"
	local path="$2"
	
	if [[ $path == $prefix* ]]; then
		true
	else
		false 
	fi
}

function makeRelative {
	local location="$1"
	local path="$2"
	
	if isSubpath "$location" "$path" ; then
		relativePath=${path#"$location"}
	else
		echo "ASSERTION: Error in micsync script. $path is not $location subpath! Please inform author."
	fi
}

function normalise {
	local pth="$1"
	local firstChar=${pth:0:1}	
	
	if [[ $firstChar == '"' ]]; then
		pth="${pth%\"}"
		pth="${pth#\"}"
		echo "$pth"
		echo "DONEXX"
		local len=${#pth}
		local elem=${#pth[*]}
		echo "LEN=$len ELEM=$elem"
		((len=$len*$elem-2))
		echo "LEN=$len"
		pth=${pth:1:len}
		echo "pthXX=$pth"
	fi
	echo "$pth"
	echo "$(realpath "$pth")"
}

function itemSelection {
	local counter=0
	local input=-1
	if [[ "$#" -gt 1 ]] ; then
		for item in "$@" ; do
			((counter++))
			echo "$counter $item"
		done
		while [[ ( ("$input" -lt 1) || ("$input" -gt "$#") ) ]]; do
			read -a inputArray -p "Type from 1 to $# " 
			input=${inputArray[0]}
		done
		selectedItem=${!input}	
	else
		selectedItem=$1
	fi
}

function findInWorkingAndBackup {
	local path="$1"
	local normalised=()
	local cfgFiles=$(getCfgFiles)
	local foundHere=false
	local foundCfgFiles=()
	FOUND_WORKING=()
	FOUNT_BACKUP=()	

	for cfgFile in $cfgFiles ; do
		source $cfgFile
		foundInWorking=false
		foundInBackup=false
		for work in "${WORKING[@]}" ; do
			normalised=$(normalise "$work")	
			if $(isSubpath "$normalised" "$path") ; then
				foundInWorking=true
			fi
		done
		for backup  in "${BACKUP[@]}" ; do
			normalised=$(normalise "$backup")	
			if $(isSubpath "$normalised" "$path") ; then
				foundInBackup=true
			fi
		done
		if [[ $foundInBackup || $foundInWorking ]]; then
			foundCfgFiles+=($cfgFile)	
		fi
	done
	
	if [[ ${#foundCfgFiles[@]} -gt 1 ]]; then
		echo "Choose configuration file:"
		itemSelection "${foundCfgFiles[@]}"
		local selectedCfgFile=$selectedItem
		echo "Configurafion file: $selectedCfgFile"
	elif [[ ${#foundCfgFiles[@]} -eq 1 ]]; then
		local selectedCfgFile=${foundCfgFiles[0]}
		echo "Configurafion file: $selectedCfgFile"
	else
		echo "Path: $path not found in configuration files:"
		for cfgFile in cfgFiles ; do
			echo "$cfgFile"
		done
	  exit 	
	fi


	source $selectedCfgFile
	local i=0
	for work in "${WORKING[@]}" ; do
		normalised=$(normalise "$work")	
		WORKING[i]="$normalised"
		((i++))
		if $(isSubpath "$normalised" "$path") ; then
			FOUND_WORKING+=($normalised)
		fi
	done
	i=0
	for backup  in "${BACKUP[@]}" ; do
		normalised=$(normalise "$backup")	
		BACKUP[i]="$normalised"
		((i++))
		if $(isSubpath "$normalised" "$path") ; then
			FOUND_BACKUP+=($normalised)
		fi
	done
	
	NUM_W=${#WORKING[@]}
	NUM_B=${#BACKUP[@]}
	NUM_F_W=${#FOUND_WORKING[@]}
	NUM_F_B=${#FOUND_BACKUP[@]}
}

function backupRsync {
	local src=$1
	local dst=$2
	if [[ $ASKMODIFIED ]]; then
		echo "Func backupRsync askmodified src=${src}, dst=${dst}."
	else
		echo "Func backupRsync src=${src}, dst=${dst}."
	fi	
}

function backup {
	for path in "$@" ; do
		echo "$path"
		path=$(normalise $path)
		echo "TEST PATH"
		echo "$path"
		findInWorkingAndBackup "$path"
	echo "TEST"
	echo "$NUM_W $NUM_B"	
	echo "$NUM_F_W $NUM_F_B"	

		if [[ ($NUM_W -eq 0) || ($NUM_B -eq 0) ]]; then
			echo "Error: Neither number of WORKING nor BACKUP can	be 0. Currently ${#WORKING[@]}, ${#WORKING[@]}. Repair configuration file."
		else
			if [[ ( ($NUM_F_W -eq 0) && ($NUM_F_B -eq 1) ) || ( ($NUM_F_W -eq 1) && ($NUM_F_B -eq 0) ) ]]; then
				echo "Error: There must be only one working or only one backup defined for path: ${path}. Repair configuration file."
			else
				if [[ ($NUM_F_W -eq 1) ]]; then
					makeRelative "$FOUND_WORKING[0]" "$path"
					for backup in "${BACKUP[@]}" ; do
						backupRsync "$path" "${backup}${relativePath}"
					done
				elif [[ ($NUM_F_B -eq 1) ]]; then
					if [[ (${#WORKING[@]} -gt 1) ]]; then
						echo "Choose which WORKING to use as backup operation source:"
						itemSelection "${WORKING[@]}"	
					  local working="$selectedItem"	
					else 
 						local working="${WORKING[0]}"	
					fi	
					echo "WORKING: $working"
					makeRelative "$FOUND_BACKUP[0]" "$path"
					for backup in "${BACKUP[@]}" ; do
						backupRsync "${working}${relativePath}" "${backup}${relativePath}"
					done
				else
					echo "ASSERTION: Error in micsync script. NUM_F_W=${NUM_F_W}, NUM_F_B=${NUM_F_B}. Please inform author."
				fi
			fi
		fi	
	done
}

function backupParse {
	paths=()
	ASKMODIFIED=true
	while [[ $# -gt 0 ]] ; do
		opt="$1"
		case $opt in
			-m)
				ASKMODIFIED=false
				shift
			;;
			*)
				paths+=('"'"$1"'"')
				shift
			;;
		esac
	done
	backup "${paths[@]}"
}

function workParse {
	paths=()
	while [[ $# -gt 0 ]] ; do
		opt="$1"
		case $opt in 
			-m)
				shift 
			;;
			-d)
				shift 
			;;
			-D)
				shift 
			;;
			*)
				paths+=('"'"$1"'"')
				shift
			;;
		esac
	done
}


function transferParse {
	paths=()
	while [[ $# -gt 0 ]] ; do
		opt="$1"
		case $opt in 
			-m)
				shift 
			;;
			-d)
				shift 
			;;
			-D)
				shift 
			;;
			*)
				paths+=('"'"$1"'"')
				shift
			;;
		esac
	done
}

function treeParse {
	paths=()
	while [[ $# -gt 0 ]] ; do
		paths+=('"'"$1"'"')
		shift
	done
}

function printhelp {
	echo "helpful help"
	echo $@
}

if [[ "$1" ==  "--backup" ]] ; then
	shift
	backupParse "$@"
elif [[ "$1" == "--work" ]] ; then
	shift
	workParse "$@"
elif [[ "$1" == "--transfer" ]] ; then
	shift
	transferParse "$@"
elif [[ "$1" == "--tree" ]] ; then
	shift
	treeParse "$@"
else
	printhelp
fi

