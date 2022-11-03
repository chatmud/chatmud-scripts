#!/bin/bash

# ChatMUD curl script

temp_dir="/home/${USER}/moo/yourmoo/tmp"

OUT=$(firejail --quiet --noprofile --seccomp --private=${temp_dir} /usr/bin/curl -s --show-error "$@") || exit $?
if jq -e type >/dev/null 2>&1 <<<"$OUT"; then
    echo "$OUT" | sed -E "s/(\xe2\x80\x9d)/\\\\\"/g;s/(\xe2\x80\x9c)/\\\\\"/g" | /usr/local/bin/unidecode | recode html
else
	echo "$OUT" | /usr/local/bin/unidecode | recode html
fi
exit $?