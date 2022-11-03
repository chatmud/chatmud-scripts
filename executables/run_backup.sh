#!/bin/bash

# Extract and launch a database from the backup directory.
# Frontend to this is @run-backup/@run-snapshot in-MOO - it passes the date and time as arguments to this script
# Set backup_dir to the location in which your backups live;
# and set snapshot_dir to the location in which the newly launched database should be copied and subsequently ran from. The restart script should be present in that directory.
# Finally, set moo to your MOO's database name
# WARNING: The MOO name is used when interpolating the database file name, as well as the new database to run. It is case sensitive.

# Check for the presence of 7zip on the system.

if ! command -v 7za &> /dev/null
then
    echo "7-zip could not be found. Exiting."
    exit
fi

day=$1
time=$2
moo="yourmoo"
backup_dir="/home/${USER}/moo/${moo}/database_backups"
snapshot_dir="/home/${USER}/moo/${moo}-Snapshot"

7za e "${backup_dir}/${DAY}/${TIME}" -o${snapshot_dir} -y
cp ${snapshot_dir}/${moo}.db ${snapshot_dir}/${moo}-snapshot.db
cd ${snapshot_dir}
./restart.sh > /dev/null
echo "Database started"