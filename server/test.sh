#!/bin/bash

set -u

host=$1

if [ "${host}" = "" ]; then
	echo "error: host"
	exit 1
fi

KEY="fedcba9876543210fedcba9876543210"
MAGIC="0123456789abcdef0123456789abcdef"
IV="00000000000000000000000000000000"

epoc=$(date +%s | tr -d '\n')
cipher=$(echo -n ${MAGIC}${epoc} | openssl aes-128-ctr -e -K ${KEY} -iv ${IV} -nosalt -nopad)

apikey=${IV}$(echo -n ${cipher} | xxd -p -c 128)
image=$(base64 -w0 ./201905101119-77957.png)

# success
echo {\"image\": \"${image}\", \"tsumo\": \"true\", \"apikey\": \"${apikey}\", \"version\": \"1\" } | curl -X POST -H "Content-Type: application/json" -d @-  ${host}/dev/score
