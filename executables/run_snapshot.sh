#!/bin/bash

# A watered down version of run_backup.sh, but for the live database only.
# Frontend to this is @run-backup/@run-snapshot in-MOO.
# Set live_dir to the location in which your MOO database lives;
# and set snapshot_dir to the location in which the live database should be copied and subsequently ran from.
# Finally, set moo to your MOO's database name
# WARNING: The MOO name is used when interpolating the database file name, as well as the new database to run. It is case sensitive.

moo="yourmoo"
live_dir="/home/${USER}/moo/${moo}"
snapshot_dir="/home/${USER}/moo/${moo}-Snapshot"

cp ${live_dir}/${moo}.db ${snapshot_dir}/${moo}-snapshot.db
cd ${snapshot_dir}
./restart > /dev/null
echo 'Database running.'