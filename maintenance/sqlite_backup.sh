#!/bin/bash
# Backup SQLite databases.
# Set basedir to the directory for backups;
# and set db_path to the directory that contains your SQLite databases.

basedir="/home/${USER}/moo/yourmoo/database_backups"
db_path="/home/${USER}/moo/yourmoo/files/databases"
temp_store="/tmp/moo_sqlite"
dirname=$(date +"%m_%d_%y")
destination="${basedir}/${dirname}"
filename=$(date +"sqlite_%H.%M")

if [ ! -d "${destination}" ]; then
mkdir ${destination}
fi

if [ ! -d "${temp_store}" ]; then
mkdir ${temp_store}
fi

cd ${db_path}

for i in *.sqlite; do
    [ -f "$i" ] || break
sqlite3 ${i} ".backup '$temp_store/${i}'"
done

7z a -t7z -m0=lzma -mx=9 -mfb=128 -md=64m -ms=on "${destination}/${filename}.7z" ${temp_store}/*
rm -rf ${temp_store}
