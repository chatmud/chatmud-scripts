#!/bin/bash
# A basic restart script.
# This does not perform any database rotation, and it relies upon your MOO's database (as well as the database being checkpointed) be named the same.
# Ensure you have git installed and the currently working directory has been initialized as a git repository (git init).

moo="yourmoo"
port=7777
now=$(date +"%m_%d_%Y_%H.%M.%p")
normal=$(tput sgr0)
red=$(tput setaf 1)

echo "${red}Creating Git backup of logs and database...${normal}"
git add ${moo}.db
git add logs

git commit -m "Server restart: ${now}"

echo "${red}Rotating log files...${normal}"

mv logs/${moo}.log ../backups/logs/${moo}_${now}.log

echo "${red}Starting ${moo}...${normal}"
echo `date`: RESTARTED >> logs/${moo}.log

# Start with an empty environment for security

env -i ./moo -l /home/${USER}/moo/${moo}/logs/${moo}.log ${moo}.db ${moo}.db ${port} & export MOO_PID=$!

echo ${MOO_PID} > ${moo}.pid
echo "${green}Started ${moo}!${normal}"