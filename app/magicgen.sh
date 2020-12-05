#!/bin/bash

cat ../../tile-score/env/env.yml | awk '/MAGIC/ {print "export const MAGIC = \x27"$2"\x27;"}' > magic.js

