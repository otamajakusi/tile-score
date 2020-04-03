#!/bin/bash

set -u

host=$1

if [ "${host}" = "" ]; then
	echo "error: host"
	exit 1
fi

KEY=$(cat ../env/env.yml | awk '/KEY/ {print $2}')
MAGIC=$(cat ../env/env.yml | awk '/MAGIC/ {print $2}')
IV="00000000000000000000000000000000"

epoc=$(date +%s | tr -d '\n')
cipher=$(echo -n ${MAGIC}${epoc} | openssl aes-128-ctr -e -K ${KEY} -iv ${IV} -nosalt -nopad)

apikey=${IV}$(echo -n ${cipher} | xxd -p -c 128)
image=$(base64 -w0 ./201905101119-77957.png)

# success
echo {\"image\": \"${image}\", \"tsumo\": \"true\", \"apikey\": \"${apikey}\", \"version\": \"1\" } | curl -X POST -H "Content-Type: application/json" -d @-  ${host}/dev/score
