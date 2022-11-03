#!/bin/bash

# Return how many connections have been made to the MOO since its last restart, assuming logs are rotated

TOTAL=$(tac "/home/${USER}/moo/logs/yourmoo.log" | grep -h -m 1 -E '^[a-zA-Z]{3} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}: (ACCEPT|CONNECT): \#-[0-9]{1,6} .+$' | awk '{print $5}')
echo ${TOTAL:2:100}
