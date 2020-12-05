#!/bin/bash

KEY=$(python -c "import yaml; print(yaml.load(open('../env/env.yml').read())['KEY'])")
./node_modules/jcrypto/bin/jcrypto.js -a aes -k ${KEY} -o wbaes.js -e hex
echo "exports.Aes = Aes;" >> wbaes.js
