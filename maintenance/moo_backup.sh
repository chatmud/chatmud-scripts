#!/bin/bash
# Compress and copy a version of the live database to a directory.
# Presently, this creates a directory for the date, and then names the database backup with the hour in which it was taken,
# although you can configure it to backup in whatever way you see fit.
# Ideally, this script will be launched every x-interval via crontab (not from the MOO via exec()!)

dirname=$(date +"%m_%d_%y")
filename=$(date +"yourmoo_%H.%M")
basedir="/home/${USER}/moo/yourmoo/database_backups"
db_path="/home/${USER}/moo/yourmoo/yourmoo.db"
destination="${basedir}/${dirname}"

if [ ! -d "${destination}" ]; then
mkdir ${destination} > /dev/null
fi

7z a -t7z -m0=lzma -mx=9 -mfb=128 -md=64m -ms=on "${destination}/${filename}.7z" ${db_path}

# Delete backups older than 31 days
find ${basedir}/* -type d -mtime +31 -exec rm -rf {} \;