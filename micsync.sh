#!/bin/bash

function getCfgFiles {
	echo "$(find ./*.location -type f)"
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

#function isNumeric {
#	if [[ ("$1" =~ ^[0-9]+$) ]]; then
#		true
#	else
#		false
#	fi
#}

#echo $(isSubpath "$1" "$2")
#if $(isSubpath "$1" "$2") ; then
#	echo "true"
#else 
#	echo "false"
#fi


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
			normalised=$(realpath "$work")	
			if $(isSubpath "$normalised" "$path") ; then
				foundInWorking=true
			fi
		done
		for backup  in "${BACKUP[@]}" ; do
			normalised=$(realpath "$backup")	
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
		selectedCfgFile=$selectedItem
		echo "Chosen: $selectedCfgFile"
	elif [[ ${#foundCfgFiles[@]} -eq 1 ]]; then
		selectedCfgFile=${foundCfgFiles[0]}
	else
		echo "Path: $path not found in configuration files:"
		for cfgFile in cfgFiles ; do
			echo "$cfgFile"
		done
	  exit 	
	fi

	source $selectedCfgFile
	for work in "${WORKING[@]}" ; do
		normalised=$(realpath "$work")	
		if $(isSubpath "$normalised" "$path") ; then
			FOUND_WORKING+=($normalised)
		fi
	done
	for backup  in "${BACKUP[@]}" ; do
		normalised=$(realpath "$backup")	
		if $(isSubpath "$normalised" "$path") ; then
			FOUND_BACKUP+=($normalised)
		fi
	done
}

echo aaaaaaaaaaaa
echo $1
givenPath=$(realpath "$1")
echo $givenPath
findInWorkingAndBackup "$givenPath"
echo bbbbbbbbbbbb
echo "found working $FOUND_WORKING"
echo "found backup $FOUND_BACKUP"
#itemSelection "$@"
#echo "selectedItems $selectedItems"
#isNumeric "$1"
#	echo "$1"
#	pppp=$(isNumeric "$1")
#	echo utput
#	echo "$pppp"
#	if $(isNumeric "$1") ; then
#		echo tak
#	else 
#		echo nie
#	fi
echo ccccccccccccccccc

function backup {
	for path in "$@" ; do
		foundLocation "$path"
		
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
	for location in $(getLocations) ; do
		backup "$location" "${paths[@]}"
	done
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

