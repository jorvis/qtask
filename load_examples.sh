#!/bin/sh

# Create the database file.  If it already exists, stop
file="$HOME/.qtask.db"
if [ -f "$file" ]
then
	echo "The qtask file $file already exists.  Please remove or back-up before running this."
    exit 1
else
	echo "$file not found - Initializing"
    qtask init
fi

echo "\nCreating projects"
qtask add project Annotation
qtask add project 'T parva'

echo "\nLogging work"
qtask log "Group status meeting"
qtask log "Configured JBrowse instance" to "T parva"
qtask log "Created script to split isoforms" to "T parva"
qtask log "Generated latest annotation" to "T parva"
qtask log "Conference call with S. Smith"
qtask log "Submitted work summary for the week"
qtask log "Added EggNOG parsing script" to Annotation
qtask log "Installated latest version of HMMER" to Annotation

echo "\nDone.  Now try some of the following commands:"
echo "  qtask list projects"
echo "  qtask list Annotation work"
echo "  qtask list 'T parva' work in last 2 weeks"







