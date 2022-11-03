#!/bin/bash

# Recursively list all available backups for parsing into the @run-backup MENU in-database.
# WARNING: If your MOO is jailed, ensure you have access to the backup directory within the environment or this will fail.

moo="yourmoo"
BACKUP_DIR="/home/${USER}/moo/${moo}/database_backups"

ls -R ${BACKUP_DIR}/* | xargs -n 1 basename