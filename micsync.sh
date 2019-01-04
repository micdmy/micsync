#!/bin/bash

function getLocationFiles {
	echo "$(find /data/projects/micsync/*.location -type f)"
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

#echo $(isSubpath "$1" "$2")
#if $(isSubpath "$1" "$2") ; then
#	echo "true"
#else 
#	echo "false"
#fi

function foundLocation {
	local path="$1"
	local normalised=()
	local locationFiles=$(getLocationFiles)
	local foundHere=false
	local declare -a foundLocationFiles
	FOUND_WORKING=()
	FOUNT_BACKUP=()	
#todo declare as arrays
#todo if found in many location files, ask which to use

	for locationFile in locationFiles ; do
		source locationFile
		foundHere=false
		for work in "${WORKING[@]}" ; do
			normalised=$(realpath "$work")	
			if $(isSubpath "$normalised" "$path") ; then
				FOUND_WORKING+=($normalised)
				foundHere=true
			fi
		done
		for backup  in "${BACKUP[@]}" ; do
			normalised=$(realpath "$backup")	
			if $(isSubpath "$normalised" "$path") ; then
				FOUND_BACKUP+=($normalised)
				foundHere=true
			fi
		done
		if $foundHere ; then
			foundLocationFiles+=($locationFile)	
		fi
	done
}

function selectItem {
	local counter=0
	local input=-1
	if [[ "$#" -gt 1 ]] ; then
		for item in "$@" ; do
			echo "$counter $item"
			((counter++))
		done
		while "$input" -lt 0 -a $ "$input" -lt "$#"
	else
		echo hhh
		echo $1
		echo hhh2
	fi
}
echo aaaaaaaaaaaa
echo "$#"
selectItem "$@"
echo bbbbbbbbbbbb

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

