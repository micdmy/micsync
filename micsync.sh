#!/bin/bash

function getLocations {
	echo "$(find /data/projects/micsync/*.location -type f)"
}

function foundLocation {
	local path="$1"

	for location in $(getLocations) ; do
		source location
		for work in "${WORKING[@]}" ; do
			
		done
	done
}

function backup {
	source "$1"
	shift

	for path in "$@" ; do

	done
	echo wokrings:
	echo "${WORKING[@]}"
  echo baskups
	echo "${BACKUP[@]}"

	echo "paths:"
	echo "$@"
	echo "$ASKMODIFIED"
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

